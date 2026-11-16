# Painel PHOENIX + HYDRA

Dashboard pública de gestão dos clãs PHOENIX e HYDRA (SkyTale): contribuições do mês, caixas de Gold e Coins, Sheltons, Bless Castle e Dungeon.

Os dados vêm da planilha oficial de gestão da liderança e são atualizados a cada lançamento.

## Atualização (liderança)
`tools/` tem os scripts que geram o `index.html` a partir da planilha exportada em .xlsx:

```
python3 tools/build_data.py planilha.xlsx data.json
DASH_PASSWORD='senha-do-cla' python3 tools/render.py data.json index.html
```

A página é pública. As seções Caixas, Bless Castle e Dungeon (e os saldos de caixa do Resumo) vão criptografadas (AES-256-GCM, chave PBKDF2-SHA256 com 600 mil iterações) e só abrem com a senha do clã. A senha não fica salva no repositório.
