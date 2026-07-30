"""Release ativa e autoritativa da edição local do ATRIO."""

from atrio_api import __version__
from atrio_api.domain import ReleaseEnvelope


MANIFEST_SHA256 = (
    "f9f81d9d41bf3c485fefbb5e1f483e74f671117e5d020ee4157210d8feb56199"
)
NORMATIVE_BUNDLE_SHA256 = (
    "7ca7a772ec0912dc75bef351dad958631cd3a3ceeed36efaebedc08366c2342f"
)

ACTIVE_RELEASE = ReleaseEnvelope(
    release_id=(
        f"atrio-local-{__version__}-"
        f"{MANIFEST_SHA256[:8]}-{NORMATIVE_BUNDLE_SHA256[:8]}"
    ),
    atrio_api_version=__version__,
    corpus_version="1.5.0",
    ratio_version="7.0.0",
    cerne_module_version="1.2.0",
    cerne_service_build="0.2.0",
    lux_version="6.0.0",
    atrio_pii_version="1.0.0",
    prompt_bundle_hash=NORMATIVE_BUNDLE_SHA256,
    schema_version="1.0.0",
)
