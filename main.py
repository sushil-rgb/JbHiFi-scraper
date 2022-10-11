from tools import JbHiFi
import pandas as pd


jbhifi_url = "https://www.jbhifi.com.au/collections/electric-transportation/escooters"

jbhifi = JbHiFi(jbhifi_url).allProductLinks()

d = {"Name": jbhifi[1],
     "Price": jbhifi[2],
     "Link": jbhifi[3],
     "Image": jbhifi[4]
    }


df = pd.DataFrame(data=d)
df.to_excel(f"JBHiFi {jbhifi[0]} database.xlsx", index=False)