from tools import JbHiFi
import pandas as pd


jbhifi_url = "https://www.jbhifi.com.au/collections/mobile-phones"

jbhifi = JbHiFi(jbhifi_url).allProductLinks()

# Initilazing the prduct value:
category = jbhifi[0]
product_name = jbhifi[1]
product_original_price = jbhifi[2]
product_discount_price = jbhifi[3]
product_reviews = jbhifi[4]
product_link = jbhifi[5]
product_image = jbhifi[6]


d = {"Name": product_name,
         "Original Price": product_original_price,
         "Discount Price": product_discount_price,
         "Reviews": product_reviews,
         "Link": product_link,
         "Image": product_image
        }

df = pd.DataFrame(data=d)
   
df.to_excel(f"JBHiFi {category} database.xlsx", index=False)
print(f"{category} database saved.")
