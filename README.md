# worn-wear-watcher
## What is this?
worn-wear-watcher checks [Worn Wear](https://www.wornwear.com) (used Patagonia clothing) for a list of specified items and notifies the user via email if any of the items are available. These checks can be made at any arbitray interval.

High demand items listed on the site are bought very quickly and this strategy helps if a user is looking for a specifc item.

## How it works
A list of [search urls, like this,](https://wornwear.patagonia.com/shop/search?size=32&category=Pants&q=performance%20jeans) for desired items are provided by the user in `url_list`. BeautifulSoup is used to parse the response and record how many of the specified items are available. If the number of items available is greater than the previous number, an email will be created and sent, indicating that a new item just got added.

## How to run
1. The email should be changed so you can email yourself

`to = "tyler.a.martin12@gmail.com"`
`sender = "tyler.a.martin12@gmail.com"`

For the gmail API, follow the [python gmail quickstart guide](https://developers.google.com/gmail/api/quickstart/python)

2. Add your desired items to `url_list.txt`, like the following:
```
shop/search?size=L&q=fjord
shop/search?q=black%20hole%20cube
```
These urls truncated and omits the base url of `https://wornwear.patagonia.com/` for brevity

3. Add `watch_job.py` to your cron jobs or task scheduler:

For example, this cron jobs runs every 10 minutes:
`*/10 * * * * cd /Users/tyler/Documents/programming/worn_wear/worn-wear-watcher && /Users/tyler/anaconda3/bin/python /Users/tyler/Documents/programming/worn_wear/worn-wear-watcher/watch_job.py >> /Users/tyler/Documents/programming/worn_wear/worn-wear-watcher/cron_out.txt  2>&1`