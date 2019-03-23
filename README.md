# worn-wear-watcher
## What is this?
worn-wear-watcher checks [Worn Wear](https://www.wornwear.com) (used Patagonia clothing) for a list of specified items and notifies the user via email if any of the items are available. These checks can be made at any arbitray interval.

High demand items listed on the site are bought very quickly and this strategy helps if a user is looking for a specifc item.

## How it works
A list of [search urls](https://wornwear.patagonia.com/shop/search?size=32&category=Pants&q=performance%20jeans) for desired items are provided by the user in `url_list`. BeautifulSoup is used to parse the response and record how many of the specified items are available. If the number of items available is greater than the previous number, an email will be created and sent, indicating that a new item just got added.

## Install before running
###### BeautifulSoup 
`pip install beautifulsoup4`
###### apscheduler
`pip install apscheduler`
###### httplib2
`pip install httplib2`
###### oauth2client
`pip install --upgrade oauth2client`
###### apiclient
`pip install apiclient`
###### google
`pip install --upgrade google-api-python-client`
`pip install gflags`
`pip install uritemplate`
###### gmail API
Follow the [python gmail quickstart guide](https://developers.google.com/gmail/api/quickstart/python)

## What to modify in watch.py
1. The email should be changed so you can email yourself (line 99)

`to = "tyler.a.martin12@gmail.com"`
`sender = "tyler.a.martin12@gmail.com"`

2. The list of items can be changed (line 111)

`url_list.append('https://wornwear.patagonia.com/shop/search?size=32&category=Pants&q=performance%20jeans')`

3. The execution interval can be changed to any interval (line 147)

`scheduler.add_job(my_worker.job, 'interval', minutes=20)`

## How to run
From the command line, execute:

`$ python watch.py`

It can also be ran remotely:

`$ python watch.py --noauth_local_webserver`

If an email is sent, the line below will be printed:

`Message Id: 169aa22eefe701a6`

Each time it is executed, the following message will be printed:

`script ran at Saturday, 23. March 2019 10:44AM`

`[0, 1, 0]`

The list above corresponds to how many of each item (urls) are available

## Sources for code
### gmail api
code adapted from [stackover user 'apadana'](https://stackoverflow.com/questions/37201250/sending-email-via-gmail-python/37267330)
