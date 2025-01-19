import apache_beam as beam

def transform_data(element):
    """Función de transformación simple."""
    return {"number": element, "square": element * element}

def run():
    """Pipeline ETL básico."""
    with beam.Pipeline() as pipeline:
        (
            pipeline
            | 'Crear datos' >> beam.Create([1, 2, 3, 4, 5])
            | 'Transformar datos' >> beam.Map(transform_data)
            | 'Imprimir resultados' >> beam.Map(print)
        )

if __name__ == "__main__":
    run()
