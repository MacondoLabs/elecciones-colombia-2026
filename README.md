# Elecciones Colombia 2026

Análisis del resultado de elecciones presidenciales 2026

> "En Dios confio, todos los demás traen datos."
>
> W. Edwards Deming

## Análisis

Publicamos la primera lectura de Barranquilla en la presidencial 2026. Spoiler: Cepeda ganó, sí. Pero lo importante no es solo quién quedó primero: es cuánto se apretó la ciudad desde 2022. Hilo con los extremos 🗺️👇

El marco: en 2022 Petro ganó Barranquilla con 51,9%. En 2026 Cepeda ganó con 47,0%. La izquierda creció en votos absolutos —256 mil → 281 mil— pero perdió casi 5 puntos de peso electoral.

La verdadera historia está al otro lado: la derecha se compactó. En 2022 Fico + Rodolfo sumaban 206 mil votos. En 2026 Abelardo solo llegó a 272 mil. Lo que antes estaba dividido, ahora apareció como bloque.

El margen se evaporó. Petro le ganó a Fico+Rodolfo por casi 49.600 votos. Cepeda le ganó a Abelardo por apenas 8.792. Barranquilla siguió siendo ganable para la izquierda, pero dejó de ser cómoda.

La participación también cambió el partido: pasó de 43,8% en 2022 a 50,7% en 2026. Entraron más de 105 mil votantes adicionales. Ese nuevo voto no fue un cheque en blanco para el Pacto.

Fajardo no fue la sorpresa: quedó casi igual en proporción, 3,30% → 3,39%. Paloma tampoco rompió: 1,91% en Barranquilla. El voto duro de derecha no se expresó por la vía uribista clásica: lo absorbió Abelardo.

La hipótesis a probar barrio por barrio: Cepeda sostiene mejor el sur/suroccidente popular; Abelardo crece en zonas de clase media, norte, corredores comerciales y voto aspiracional. Pero eso hay que medirlo con puestos de votación, no con intuición.

Conclusión: Barranquilla no giró completamente. Se apretó. Cepeda ganó la foto; Abelardo ganó el movimiento. La segunda vuelta se juega en abstención, voto Fajardo/Paloma y barrios donde el voto petrista dejó de ser automático.

Metodología correcta: resultados por mesa/puesto + Divipole 2026 georreferenciada + polígonos oficiales de barrios/localidades. Cada puesto se asigna al barrio donde cae su coordenada. La Registraduría publica Divipole con geolocalización de puestos; Barranquilla tiene capa oficial de barrios.

Limitación clave: esto mide el voto registrado en puestos ubicados en un barrio, no necesariamente la residencia exacta del votante. Para no vender humo, el mapa debe decir “puesto ubicado en X barrio”, no “todo el barrio votó X”.

## Links externos

El análisis se puede acceder y compartir desde

- [Twitter/X](https://x.com/3scorciav/status/2062150697143926884?s=20)

- [Post en LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7467917621511000064)

## Plomería de Datos

El codigo usado para el análisis esta [aquí](./analisis.py), para correrlo en otras ciudades:

```python
MEDELLIN = City("MEDELLIN", dept_code=1, mun_code=1)   # ejemplo: validar códigos
CALI = City("CALI", dept_code=31, mun_code=1)          # ejemplo: validar códigos
```

### Mapeo de datos

La parte del [mapeo/gráficas](./color_mapping.py)

```bash
python color_mapping.py \
  --input outputs/barranquilla_by_barrio_long.csv \
  --city Barranquilla \
  --output outputs/barranquilla_color_mapping.csv \
  --format wide 
```

### Detalles

JSON output:

```bash
python color_mapping.py \
  --input outputs/barranquilla_by_barrio_long.csv \
  --city Barranquilla \
  --output outputs/barranquilla_color_mapping.json
```

Expected long format from `analisis.py`

```csv
city,area_id,area_name,candidate,votes
Barranquilla,080010001,El Prado,Iván Cepeda,1234
Barranquilla,080010001,El Prado,Abelardo de la Espriella,1456
```

Expected wide format:

```csv
city,area_id,area_name,cepeda_votes,abelardo_votes
Barranquilla,080010001,El Prado,1234,1456
```

Output includes:

```csv
city,area_id,area_name,abelardo_votes,cepeda_votes,winner_key,winner_label,fill_color
Barranquilla,080010001,El Prado,1456,1234,ABELARDO,Abelardo,#071A78
```

Color theme:

```
ABELARDO = "#071A78"  # deep blue
CEPEDA   = "#B63A2E"  # brick red
NO_DATA  = "#D8D2C4"  # warm gray
```

## Agradecimientos

Hecho por [@escorciav](https://github.com/escorciav), con amor, paciencia e IA
