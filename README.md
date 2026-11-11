# Painel PHOENIX + HYDRA

Dashboard pública de gestão dos clãs PHOENIX e HYDRA (SkyTale): contribuições do mês, caixas de Gold e Coins, Sheltons, Bless Castle e Dungeon.

Os dados vêm da planilha oficial de gestão da liderança e são atualizados a cada lançamento.

## Atualização (liderança)
`tools/` tem os scripts que geram o `index.html` a partir da planilha exportada em .xlsx:

```
python3 tools/build_data.py planilha.xlsx data.json
python3 tools/render.py data.json index.html
```
