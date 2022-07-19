import json, logging, sys
import azure.functions as func


def main(blobin: func.InputStream, blobout: func.Out[bytes], context: func.Context):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {blobin.name}\n"
                 f"Blob Size: {blobin.length} bytes")
    logging.info('Python Blob trigger function processed %s', blobin.name)
    input_ioc = [value + '/32' for value in list(blobin.read().decode().split('\r\n')) if len(value) > 7]

    gdc_config_path = f'{context.function_directory}/gdc_config.json'
    gdc_header = {"version": "1.0", "description": "Black List", "objects": []}
    gdc_config = {}
    try:
        with open(gdc_config_path, 'r') as f:
            gdc_config = json.load(f)
            logging.info(f"Loaded GDC Config: {gdc_config}")
    except OSError as e:
        logging.error(f'Error: Unable to read config.\n{e}')
        sys.exit(1)
    except Exception as e:
        logging.error(f'Generic Error: {e}')
        sys.exit(2)

    # GET DATA and write as list in ranges
    gdc_config['ranges'] = input_ioc
    gdc_header['objects'] = [ gdc_config ]

    # Write GDC object to the blob
    blobout.set(json.dumps(gdc_header, indent=2).encode())