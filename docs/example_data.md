# Example Data

Snippets of example data, useful for testing and understanding format, are detailed below.

All data sets can be found in The directory [src/industrial_classification/data](https://github.com/ONSdigital/sic-classification-library/blob/main/src/industrial_classification/data)

## Example SIC Lookup Data

[Example SIC Lookup Data CSV](https://github.com/ONSdigital/sic-classification-library/blob/main/src/industrial_classification/data/example_sic_lookup_data.csv)

### SIC Lookup - Example Rows

|description                 |label|bridge|
|----------------------------|-----|------|
|Insulating activities       |43290|QRSUY |
|Construction of harbours    |42910|QRSUZ |
|Installation and maintenance|43220|QRSVQ |
|Street lighting installation|43210|QRSVR |

## Example Rephrased SIC Data

[Example Rephrased SIC Data CSV](https://github.com/ONSdigital/sic-classification-library/blob/main/src/industrial_classification/data/example_rephrased_sic_data.csv)

### Rephrased SIC - Example Rows

| input_code | sic_code | input_description                                                                                                       | llm_rephrased_description | reviewed_description        |
|------------|----------|-----------------------------------------------------------------------------------------------------------------------|---------------------------|-----------------------------|
| 01110      | 01110    | {Code: 01110, Title: Growing of cereals (except rice), leguminous crops and oil seeds, Example activities: Barley growing, Bean growing, Broad bean growing} | Crop farming              | Crop growing                |
| 01120      | 01120    | {Code: 01120, Title: Growing of rice, Example activities: Rice growing}                                                 | Rice farming              | Rice growing                |
| 01130      | 01130    | {Code: 01130, Title: Growing of vegetables and melons, roots and tubers, Example activities: Alliaceous vegetable growing, Artichoke growing, Asparagus growing} | Vegetable and melon farming | Vegetable and melon growing |
| 01140      | 01140    | {Code: 01140, Title: Growing of sugar cane, Example activities: Sugar cane growing}                                     | Sugar cane farming        | Sugar cane growing          |
