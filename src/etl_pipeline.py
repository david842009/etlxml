import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.jdbc import WriteToJdbc
import typing
import os
import xml.etree.ElementTree as ET

# Define NamedTuples for table schemas
PropertiesRow = typing.NamedTuple('PropertiesRow', [
    ('ubicacion', str),
    ('type', str),
    ('purpose', str),
    ('price', int),
    ('code', int),
    ('mail_contact', str),
    ('phone_contact', int)
])

UsersRow = typing.NamedTuple('UsersRow', [
    ('code', int),
    ('mail_contact', str)
])

beam.coders.registry.register_coder(PropertiesRow, beam.coders.RowCoder)
beam.coders.registry.register_coder(UsersRow, beam.coders.RowCoder)

# Helper function to clean data
def clean_data(element):
    return element.strip() if element else None

class ParseXML(beam.DoFn):
    def process(self, element):
        try:
            tree = ET.ElementTree(ET.fromstring(element))
            root = tree.getroot()

            for property_elem in root.findall('.//listing'):
                try:
                    property_data = {
                        'state': clean_data(property_elem.find('state').text),
                        'city': clean_data(property_elem.find('city').text),
                        'colony': clean_data(property_elem.find('colony').text),
                        'street': clean_data(property_elem.find('street').text),
                        'external_num': clean_data(property_elem.find('external_num').text),
                        'code': int(clean_data(property_elem.find('code').text)),
                        'type': clean_data(property_elem.find('type').text),
                        'purpose': clean_data(property_elem.find('purpose').text),
                        'price': int(clean_data(property_elem.find('price').text)),
                        'mail_contact': clean_data(property_elem.find('mail_contact').text),
                        'phone_contact': int(clean_data(property_elem.find('phone_contact').text))
                    }
                    yield property_data
                except AttributeError:
                    yield beam.pvalue.TaggedOutput('errors', element)
        except ET.ParseError as e:
            print(f"ParseError: {e}")

def format_properties(element):
    ubicacion = f"{element['state']}-{element['city']}-{element['colony']}-{element['street']}"
    return PropertiesRow(
        ubicacion=ubicacion,
        type=element['type'],
        purpose=element['purpose'],
        price=element['price'],
        code=element['code'],
        mail_contact=element['mail_contact'],
        phone_contact=element['phone_contact']
    )

def format_users(element):
    return UsersRow(
        code=element['code'],
        mail_contact=element['mail_contact']
    )

def clean_price(record):
    try:
        # Convertir el precio a float y verificar que esté en un rango válido
        price = float(record['price'])
        if price < 0 or price > 100_000_000:  # Ajusta el rango según tu caso
            record['price'] = None  # Asigna un valor nulo si está fuera de rango
        else:
            record['price'] = price
    except (ValueError, TypeError):
        record['price'] = None  # Maneja errores de conversión
    return record

def run(input_path):
    pipeline_options = PipelineOptions()
    with beam.Pipeline(options=pipeline_options) as p:
        # Read the XML file
        xml_data = (
            p
            | 'Read XML File' >> beam.io.ReadFromText(input_path)
            | 'Combine Lines' >> beam.CombineGlobally(lambda lines: '\n'.join(lines)).without_defaults()
        )

        # Parse the XML data
        parsed_data = xml_data | 'Parse XML' >> beam.ParDo(ParseXML()).with_outputs('errors', main='main')

        # Write properties to MySQL using JDBC
        (parsed_data['main']
         | 'Format Properties' >> beam.Map(format_properties).with_output_types(PropertiesRow)
         | 'Write Properties to MySQL' >> WriteToJdbc(
            driver_class_name='com.mysql.cj.jdbc.Driver',
            jdbc_url=f"jdbc:mysql://{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}?serverTimezone=UTC",
            username=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            table_name='tbl_properties',
            driver_jars='/path/to/mysql-connector-java.jar',
        ))

        # Write users to MySQL using JDBC
        (parsed_data['main']
         | 'Extract User Data' >> beam.Map(format_users).with_output_types(UsersRow)
         | 'Remove Duplicates' >> beam.Distinct()
         | 'Write Users to MySQL' >> WriteToJdbc(
            driver_class_name='com.mysql.cj.jdbc.Driver',
            jdbc_url=f"jdbc:mysql://{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}?serverTimezone=UTC",
            username=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            table_name='tbl_user',
            driver_jars='/path/to/mysql-connector-java.jar',
        ))

if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_PATH = os.path.join(BASE_DIR, 'data_source', 'feed.xml')

    run(INPUT_PATH)
