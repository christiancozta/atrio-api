from __future__ import annotations

import hashlib
import json
import unittest

import httpx

from atrio_api.adapters.ollama import (
    OLLAMA_ADAPTER_VERSION,
    OllamaAdapter,
    OllamaAdapterError,
    OllamaModelUnavailable,
    OllamaProtocolError,
)


_DIGEST = "sha256:" + ("a" * 64)


class OllamaAdapterTests(unittest.TestCase):
    def _adapter(self, handler, *, retries: int = 0) -> OllamaAdapter:
        client = httpx.Client(
            base_url="http://ollama:11434",
            transport=httpx.MockTransport(handler),
        )
        self.addCleanup(client.close)
        return OllamaAdapter(
            "http://ollama:11434",
            client=client,
            max_retries=retries,
            sleeper=lambda _: None,
        )

    def test_rejects_url_with_credentials_or_path(self) -> None:
        with self.assertRaises(ValueError):
            OllamaAdapter("http://user:secret@localhost:11434")
        with self.assertRaises(ValueError):
            OllamaAdapter("http://localhost:11434/api")

    def test_healthcheck_validates_protocol(self) -> None:
        adapter = self._adapter(
            lambda request: httpx.Response(200, json={"models": []})
        )
        self.assertTrue(adapter.healthcheck())

    def test_healthcheck_rejects_invalid_envelope(self) -> None:
        adapter = self._adapter(
            lambda request: httpx.Response(200, json={"unexpected": []})
        )
        with self.assertRaises(OllamaProtocolError):
            adapter.healthcheck()

    def test_model_must_be_installed(self) -> None:
        adapter = self._adapter(
            lambda request: httpx.Response(200, json={"models": []})
        )
        with self.assertRaises(OllamaModelUnavailable):
            adapter.generate("teste", model="qwen3:8b")

    def test_generate_records_safe_provenance(self) -> None:
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.url.path == "/api/tags":
                return httpx.Response(
                    200,
                    json={
                        "models": [
                            {"model": "qwen3:8b", "digest": _DIGEST}
                        ]
                    },
                )
            return httpx.Response(
                200,
                json={
                    "model": "qwen3:8b",
                    "response": "resultado",
                    "total_duration": 10,
                    "prompt_eval_count": 7,
                    "eval_count": 4,
                },
            )

        adapter = self._adapter(handler)
        result = adapter.generate(
            "entrada",
            model="qwen3:8b",
            options={"num_predict": 80},
        )

        self.assertEqual(result.content, "resultado")
        self.assertEqual(
            result.metadata.prompt_sha256,
            hashlib.sha256("entrada".encode()).hexdigest(),
        )
        self.assertEqual(result.metadata.model_digest, _DIGEST)
        self.assertEqual(
            result.metadata.adapter_version,
            OLLAMA_ADAPTER_VERSION,
        )
        payload = json.loads(requests[-1].content)
        self.assertEqual(payload["options"]["temperature"], 0.0)
        self.assertEqual(payload["options"]["seed"], 0)
        self.assertEqual(payload["options"]["num_ctx"], 40960)
        self.assertEqual(payload["options"]["num_predict"], 80)
        self.assertFalse(payload["stream"])
        self.assertEqual(result.metadata.prompt_eval_count, 7)
        self.assertEqual(result.metadata.eval_count, 4)
        self.assertGreater(result.metadata.context_headroom_tokens, 0)
        self.assertEqual(result.metadata.generation_attempts, 1)

    def test_unknown_option_is_rejected_before_generation(self) -> None:
        adapter = self._adapter(
            lambda request: httpx.Response(
                200,
                json={
                    "models": [
                        {"model": "qwen3:8b", "digest": _DIGEST}
                    ]
                },
            )
        )
        with self.assertRaisesRegex(ValueError, "não permitidas"):
            adapter.generate(
                "teste",
                model="qwen3:8b",
                options={"arbitrary": True},
            )

    def test_empty_response_is_not_success(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/tags":
                return httpx.Response(
                    200,
                    json={
                        "models": [
                            {"model": "qwen3:8b", "digest": _DIGEST}
                        ]
                    },
                )
            return httpx.Response(
                200,
                json={"model": "qwen3:8b", "response": ""},
            )

        adapter = self._adapter(handler)
        with self.assertRaises(OllamaProtocolError):
            adapter.generate("teste", model="qwen3:8b")

    def test_invalid_json_is_not_success(self) -> None:
        adapter = self._adapter(
            lambda request: httpx.Response(
                200,
                content=b"not-json",
                headers={"content-type": "application/json"},
            )
        )
        with self.assertRaises(OllamaProtocolError):
            adapter.healthcheck()

    def test_retries_transient_status(self) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            if calls == 1:
                return httpx.Response(503)
            return httpx.Response(200, json={"models": []})

        adapter = self._adapter(handler, retries=1)
        self.assertTrue(adapter.healthcheck())
        self.assertEqual(calls, 2)

    def test_does_not_retry_permanent_status(self) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(404)

        adapter = self._adapter(handler, retries=2)
        with self.assertRaises(OllamaAdapterError):
            adapter.healthcheck()
        self.assertEqual(calls, 1)

    def test_prompt_limit_is_enforced(self) -> None:
        adapter = self._adapter(
            lambda request: httpx.Response(200, json={"models": []})
        )
        adapter._max_prompt_chars = 3
        with self.assertRaisesRegex(ValueError, "limite"):
            adapter.generate("quatro", model="qwen3:8b")

    def test_context_options_are_required_and_consistent(self) -> None:
        with self.assertRaisesRegex(ValueError, "num_predict"):
            OllamaAdapter(
                "http://localhost:11434",
                default_options={"num_ctx": 128, "num_predict": 128},
            )

    def test_conservative_context_preflight_fails_before_http(self) -> None:
        calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal calls
            calls += 1
            return httpx.Response(200, json={"models": []})

        client = httpx.Client(
            base_url="http://ollama:11434",
            transport=httpx.MockTransport(handler),
        )
        self.addCleanup(client.close)
        adapter = OllamaAdapter(
            "http://ollama:11434",
            client=client,
            default_options={"num_ctx": 300, "num_predict": 32},
        )
        with self.assertRaisesRegex(ValueError, "contexto"):
            adapter.generate("x" * 32, model="qwen3:8b")
        self.assertEqual(calls, 0)

    def test_missing_token_telemetry_is_not_success(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/api/tags":
                return httpx.Response(
                    200,
                    json={
                        "models": [
                            {"model": "qwen3:8b", "digest": _DIGEST}
                        ]
                    },
                )
            return httpx.Response(
                200,
                json={"model": "qwen3:8b", "response": "resultado"},
            )

        adapter = self._adapter(handler)
        with self.assertRaisesRegex(OllamaProtocolError, "obrigatória"):
            adapter.generate("teste", model="qwen3:8b")


class ContainerSettingsTests(unittest.TestCase):
    def test_container_settings_reject_invalid_database_identifier(self) -> None:
        from atrio_api.container_runtime import ContainerSettings

        with self.assertRaises(ValueError):
            ContainerSettings.from_environment(
                {"ATRIO_DB_NAME": "atrio;drop"}
            )

    def test_container_settings_resolves_secret_files(self) -> None:
        from atrio_api.container_runtime import ContainerSettings

        settings = ContainerSettings.from_environment(
            {
                "ATRIO_REPOSITORY_ROOT": "/srv/atrio",
                "ATRIO_DB_PASSWORD_FILE": "/secrets/db",
                "ATRIO_VAULT_PASSPHRASE_FILE": "/secrets/vault",
            }
        )
        self.assertEqual(
            settings.database_password_file.as_posix(),
            "/secrets/db",
        )
        self.assertEqual(
            settings.packages_root.as_posix(),
            "/srv/atrio/packages",
        )


if __name__ == "__main__":
    unittest.main()
