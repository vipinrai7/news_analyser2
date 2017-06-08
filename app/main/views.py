from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import main
import requests
import base64
from json import loads, dump

URL_SOURCES = 'https://newsapi.org/v1/sources'
URL_HEADLINE = 'https://newsapi.org/v1/articles'
API_KEY = 'f3db3605619e43639d45d2806bcee853'

def retreive_json_data(cats):
	""" 
	"""
	file = open('sources.json','r')
	json_data = loads(file.read())
	data = []
	for items in json_data['sources']:
		category = items['category']
		name = items['name']
		desc = items['description']
		url = 'https://icons.better-idea.org/icon?url='+items['url']\
				+'&size=50..100..100'
		ids = items['id']
		if category==cats:
			part = dict(category=category, name=name, url=url , \
					desc=desc,ids=ids)
			data.append(part)
	return data


@main.route('/')
def index():
	return render_template('index.html')

@main.route('/categories')
@login_required
def categories():
    """
    """
    datas =['gaming', 'business', 'entertainment', 'general', 'science-and-nature', 'music', 'politics', 'sport', 'technology']
    return render_template('categories.html', data=datas)

@main.route('/sources/<cats>')
@login_required
def sources(cats):
    """
    """
    datas=retreive_json_data(cats)
    return render_template('sources.html',data=datas)

@main.route('/results/<ids>')
@login_required
def results(ids):
    """
    """
    response = requests.get(URL_HEADLINE, params=dict(apiKey=API_KEY, \
                                                      source=ids))
    mx = response.json()

    headlines = []
    for items in mx['articles']:
        article = {}
        article['url'] = base64.b64encode(items['url'])
        article['title'] = items['title']
        article['time'] = items['publishedAt']
        article['image'] = items['urlToImage']
        headlines.append(article)

    return render_template('results.html', headlines=headlines)


@main.route('/analytics/<url>')
@login_required
def analytics(url):
    """
    """
    url_decoded = base64.b64decode(url)
    apikey = '81a99dfe-78eb-4420-ab19-2831f0887673'
    api_url = 'https://api.havenondemand.com/1/api/sync/analyzesentiment/v2'
    data = dict(apikey=apikey, url=url_decoded)
    response = requests.get(api_url, params=data)
    json_data = response.json()

    stats = dict(json_data['sentiment_analysis'][0])
    if stats['aggregate']['score']<0 and current_user.age<18:
        flash('You are too young to access this article')
        return redirect(url_for('main.categories'))
    else:
        return render_template('analytics.html', data=stats,url=url_decoded)