import spintax
import csv
import smart_open

#Read the list of senders from the s3 bucket
def read_senders(bucket_name="inmuebles24-scraper-bucket", filename="/input/data.csv"):
    key = "AKIA3YE4AEODPFIOEN4Q"#os.environ["bucket_key"],
    secret_key = "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"
    #bucket_name = "inmuebles24-scraper-bucket"
    #filename = "/input/data.csv"

    uri = f"s3://{key}:{secret_key}@{bucket_name}{filename}"

    f = smart_open.open(uri, encoding='ISO-8859–1')

    a = [{k: str(v) for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]
    return a

#Create message for send to contact
#Format a spintax message
def format_message(msg, post, data):
    if msg != "":
        spin = spintax.spin(msg)
        format = spin.replace("[","{").replace("]","}")

        return format.format(
                      titulo = post["title"],
                      precio = post["price"],
                      zona   = post["zone"],
                      telefono=data["phone"],
					  sitio  = data["site"],
					  referencia = data["reference"]
                     )
    else:
        return ""
