import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import xml.etree.ElementTree as ET
import os

def clean_data(element):
    return element.strip()

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
                        'code': clean_data(property_elem.find('code').text),
                        'type': clean_data(property_elem.find('type').text),
                        'purpose': clean_data(property_elem.find('purpose').text),
                        'price': clean_data(property_elem.find('price').text),
                        'mail_contact': clean_data(property_elem.find('mail_contact').text),
                        'phone_contact': clean_data(property_elem.find('phone_contact').text)
                    }
                    yield property_data
                except AttributeError:
                    yield beam.pvalue.TaggedOutput('errors', element)
        except ET.ParseError as e:
            print(f"ParseError: {e}")

def format_properties(element):
    ubicacion = f"{element['state']}-{element['city']}-{element['colony']}-{element['street']}"
    return f"{ubicacion},{element['type']},{element['purpose']},{element['price']},{element['code']},{element['mail_contact']},{element['phone_contact']}"
 
def format_users(element):
    return element['mail_contact']

def run(input_path, output_path_properties, output_path_users):
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
        
        # Extract properties
        properties = (
            parsed_data['main']
            | 'Filter Properties' >> beam.Filter(lambda x: 'state' in x)
            | 'Format Properties' >> beam.Map(format_properties)
            | 'Write Properties' >> beam.io.WriteToText(output_path_properties, file_name_suffix='.txt', shard_name_template='', header='ubicacion,type,purpose,price,code,mail_contact,phone_contact')
        )
        
        # Extract users
        users = (
            parsed_data['main']
            | 'Extract User Data' >> beam.Map(format_users)
            | 'Remove Duplicates' >> beam.Distinct()
            | 'Write Users' >> beam.io.WriteToText(output_path_users, file_name_suffix='.txt', shard_name_template='', header='mail_contact')
        )


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INPUT_PATH = os.path.join(BASE_DIR, 'data_source', 'feed.xml')
    OUTPUT_PROPERTIES = os.path.join(BASE_DIR, 'output', 'properties')
    OUTPUT_USERS = os.path.join(BASE_DIR, 'output', 'users')

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PROPERTIES), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_USERS), exist_ok=True)

    run(INPUT_PATH, OUTPUT_PROPERTIES, OUTPUT_USERS)