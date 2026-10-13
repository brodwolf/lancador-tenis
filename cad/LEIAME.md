# Código-fonte do CAD

- `lancador.py`: modelo paramétrico da máquina completa (CadQuery).
- `exportar.py`, `verificar.py`: exportação e conferência da máquina completa.
- `mvp/mvp.py`: monta só o MVP (base do andar do lançador, giro, tilt, cabeça e as pernas).
- `mvp/exportar_mvp.py`: gera `1-imprimir`, `2-cortar`, `3-usinar`, `modelo` e `pecas_do_modelo_mvp.csv`.
- `mvp/verificar_mvp.py`: confere a interferência entre todas as peças do MVP nos extremos de giro e inclinação.
- `mvp/docs/`: gera os LEIAME, a lista de compras, os desenhos da elétrica, o projeto do Wokwi e o guia HTML.

```
pip install cadquery ezdxf matplotlib playwright pillow
cd cad/mvp
python3 exportar_mvp.py ../..          # arquivos de fabricação na raiz da branch
python3 verificar_mvp.py               # folgas
python3 docs/gerar_docs.py ../..       # documentação
```
