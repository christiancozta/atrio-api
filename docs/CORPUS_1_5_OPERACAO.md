# CORPUS 1.5 — operação local

## Preparação da release

1. Encerre a API anterior com `Ctrl+C`.
2. Na raiz do ATRIO, aplique as migrações:

   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass `
       -File .\packages\services\atrio_api\tools\apply_migrations.ps1
   ```

3. Inicie a API:

   ```powershell
   & .\packages\services\atrio_api\.venv\Scripts\python.exe `
       .\packages\services\atrio_api\tools\run_api.py
   ```

4. Confirme o readiness:

   ```powershell
   Invoke-RestMethod `
       -Uri 'http://127.0.0.1:8080/v1/health/ready' `
       -Method Get |
       ConvertTo-Json
   ```

O resultado esperado declara API `0.7.0`, schema `1.3.0`, pipeline CORPUS
`1.5.0` e release iniciada por `atrio-local-0.7.0-`.

## Teste pela interface

1. Abra `http://127.0.0.1:8080/`.
2. Encerre uma sessão antiga que esteja gravada no navegador.
3. Crie uma nova execução; releases antigas continuam imutáveis e não recebem
   processamento da release nova.
4. Anexe PDF, DOCX, JPEG, PNG, TIFF ou TXT.
5. Clique em **Processar documentos**.
6. Leia no lote o método de extração, quantidade de caracteres, CNJ, tipo de
   revisão e situação.
7. Se aparecer **revisão obrigatória**, escolha **Aprovar** ou **Excluir**.
8. Clique novamente em **Processar documentos**. Sem pendências, a console
   produz o artefato cifrado e muda a execução para `CORPUS_READY`.

## Significado das situações

- `registrado`: original autenticado e cifrado; ainda não foi processado;
- `pseudonimizado`: inventário e texto interno estão prontos;
- `revisão obrigatória`: OCR, sigilo ou qualidade exigem decisão humana;
- `revisado e aprovado`: documento entra no artefato final;
- `excluído da saída`: documento permanece auditável, mas não entra no
  handoff;
- `CORPUS_READY`: lote cifrado e versionado está pronto para o RATIO.

## Limites de exposição

A interface e a API recebem apenas inventário seguro. Texto extraído,
identificadores reais, mapa reversível e caminhos físicos não aparecem em
respostas, eventos ou dossiês exportados.
