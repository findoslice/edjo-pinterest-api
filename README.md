# **edjo-pinterest-api**

An application test/project I wrote for applying to [edjo](https://edjo.io)! Using selenium, it crawls and saves image links into redis before classifying them by colour code and saving them into elasticsearch. This then is available and searchable by colour code through a lightning fast API.

## Installation and configuration
This project requires [redis](https://redis.io/download), [elasticsearch](https://www.elastic.co/downloads/elasticsearch) and [google chrome](https://www.google.com/chrome/) to be installed - redis and elasticsearch must also be running while the programme is. Due to limitations in google chrome's headless feature this software is only capable of running on 64 bit linux (unless you want to set your computer on fire). 

Python3 is also required, to install the required python modules, install the requirements.txt file using the command:
```bash
pip3 install -r requirements.txt
```
it is advisable to do this in a virtual environment as a specific version of numpy is required.

In addition to these installation requirements it's also essential to configure the system variables in the `config.ini` file. It is essential to set the host/port for redis and elasticsearch to the correct ones for your system, as well as the chrome binary location to where it is on your computer. In addition, it is possible to configure which redis databases are used (so as not to interfere with others on your system), the expiry time for next page tokens in the api, and which parser beautifulsoup uses (this is not advised in case the behaviour changes).

## Usage ##
The crawler software can be ran using 2 methods, either launching the individual worker files separately, or by running the launch script (coming soon).

If you choose to employ the first method it is not overly complicated, simply run the file `scraper.py` to scrape images from pinterest and `classifier.py` to classify images and enter them into the elasticsearch database (these tasks can be ran concurrently).

To run the API, simply enter the following command into a terminal from the repo's top directory
```bash
gunicorn api:api --workers=n
```
where n is the number of api workers, there are other usable flags, but I'll let you find those for yourself.

## API usage
The API has several endpoints, these are:

- `/search`
- `/next/<token>`
- `/next/delete/<token>`
- `/count`
- `/count/all`
- `/are/you/a/tea/pot`

### `/search`
This is the main endpoint, used for searching the database of tagged images. The query is based on hex colour codes specified by the user. A request to this endpoint should have a body of the form:
```
                    {"colours" : [colour],
		     "pagesize": pagesize,
		     "expire" : expire}
```
 where the values are the following:
 
 - `[colour]`, an array of hex colour codes (i.e. #FFFFFF). Leaving this empty, not specifying it, or including an incorrectly formatted code will result in an HTTP 204 no content response.
 - `pagesize` (optional), an integer specifying the pagesize (i.e. number of images) per page.
 - `expire` (optional), an integer specifying the desired expiry time in seconds for the next page token. This defaults to 2 days and if above a configurable maximum duration it will be set to the maximum duration.

An example of this query is included in `post_loc.json` Presuming you've done everything correctly up to this point and I have written good code (a bold assumption), the response from this endpoint should look like:
```
				            {"method" : "/search",
                     "next" : pagekey,
                     "nextendpoint": "/next",
                     "expiretime" : expireduration,
                     "expires" : expiredate,
                     "expires-epochtime" : expiretime,
                     "colours" : [colour],
                     "pagesize" : pagesize,
                     "images" : [image]}
```
 where the values are the following:
 
 - `pagekey`, the token to be used for accessing the next page of results from this query
 - `expireduration`, the time in seconds from the request being returned until the next token is no longer valid
 - `expiredate`, the time and date of when the token becomes invalid, formatted as `2019/01/25 19:36:01`
 - `expiretime`, the time at which the token expires in epoch time
 - `[colour]`, the array of colours specified in the initial user request
 -  `pagesize` the size of the page
 - `[image]`, the list of pinterest cdn URLs to images found by the search

In the case where the search finds no matches in the database, this endpoint will return an HTTP 204 No content response and no response body.

### `/next/<token>`

The endpoint used to get the next page of a query sent to `/search`, where `<token>` is the the pagekey returned in the `/search` response with the key `"next"`. This endpoint takes no request body and will return a response of the form:

					         `{"method" : "/next/" + token,
                     "next" : token,
                     "nextendpoint": "/next",
                     "expiretime" : expire,
                     "expires" : expiredate,
                     "expires-epochtime" : expiretime,
                     "colours" : [colour],
                     "pagesize" : pagesize,
                     "images" : [image]}`

where the values are the following:
 - `token`, the token to be used for accessing the next page of results from this query
 - `expireduration`, the time in seconds from the request being returned until the next token is no longer valid
 - `expiredate`, the time and date of when the token becomes invalid, formatted as `2019/01/25 19:36:01`
 - `expiretime`, the time at which the token expires in epoch time
 - `[colour]`, the array of colours specified in the initial user request
 -  `pagesize` the size of the page
 - `[image]`, the list of pinterest cdn URLs to images found by the search

In the event that there are no matches to the query remaining or the token has expired, this endpoint will return an HTTP 204 No Content response and no body.
 
### `/next/delete/<token>`

The endpoint to delete a next page token, unnecessary for the user but nice to the server. Takes nothing and returns nothing except an HTTP 200 status code.

### `/are/you/a/tea/pot`

This essential endpoint confirms whether or not the server is a teapot, and will return the following response:
```
			{
			'teapot': {
					'status':'true'
				}
			}
```
and an HTTP 418 "I'm a teapot status" code.

### `/count`

 This endpoint has similar behaviour to `/search` however instead of returning a page of URLs to images, it returns the number of images in the database containing the user specified list of colours. The request body should only specify the colour terms to search for, such as:
 
 `                  {"method" : "/count",
                     "colours" : [colour],
                     "count" : count}
 `
 where `[colour]` is the list of user specified colours, and `count` is the number of database entries matching the search.

### `/count/all` ###

This endpoint just returns the number of images entered into the database, taking no body arguments and giving a response in the following form:

```
					          {"method" : "/count/all",
                     "count" : count}
```

where `count` is the number of image entries in the database.
