#!/usr/bin/python
# -*- coding:utf-8 -*-
import urllib2, io, os, sys
import chardet
from gzip import GzipFile
from StringIO import StringIO
import BeautifulSoup
from PIL import Image

CONST_HEIGHT = 340

class ContentEncodingProcessor(urllib2.BaseHandler):
  """A handler to add gzip capabilities to urllib2 requests """
  # add headers to requests
  def http_request(self, req):
 
    req.add_header("Accept-Encoding", "gzip, deflate")
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
    req.add_header("Accept", "text/html;q=0.9,*/*;q=0.8")
    req.add_header("Accept-Charset", "ISO-8859-1,utf-8;q=0.7,*;q=0.3")
    req.add_header("Connection", "close")
    req.add_header("Referer", None)
    return req

  # decode
  def http_response(self, req, resp):
    old_resp = resp
    # gzip
    if resp.headers.get("content-encoding") == "gzip":
        gz = GzipFile(
                    fileobj=StringIO(resp.read()),
                    mode="r"
                  )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)
        resp.msg = old_resp.msg
    # deflate
    if resp.headers.get("content-encoding") == "deflate":
        gz = StringIO( deflate(resp.read()) )
        resp = urllib2.addinfourl(gz, old_resp.headers, old_resp.url, old_resp.code)  # 'class to add info() and
        resp.msg = old_resp.msg
    return resp

# deflate support
import zlib
def deflate(data):   # zlib only provides the zlib compress format, not the deflate format;
  try:               # so on top of all there's this workaround:
    return zlib.decompress(data, -zlib.MAX_WBITS)
  except zlib.error:
    return zlib.decompress(data)

def getPicIds(filename):
	ret_list = []
	f = open(filename)
	try:
		ids = f.readlines()
	finally:
		f.close()
	for line in ids:
		ret_list.append(line.rstrip())
	return ret_list 

def getPicPath(picId):
	return './pics/'+picId+'.jpg'

def procPics(picidlist):
	for pic_id in picidlist:
		pic_path = getPicPath(pic_id) 
		print(pic_path)
		#read pic file
		img = Image.open(pic_path)
		(x,y) = img.size
		width = int(x * CONST_HEIGHT / y)
		small_img = img.resize((width,CONST_HEIGHT), Image.ANTIALIAS)
		#cut pic with
		box = (abs(width-208)/2,0,width-(abs(width-208)/2),CONST_HEIGHT)
		region = small_img.crop(box)
		region.save(getPicPath(pic_id+'_s'), quality=95)


def downPics(picidlist):
	url_pre = 'http://www.xxx.com/share/item/'

	encoding_support = ContentEncodingProcessor
	opener = urllib2.build_opener(encoding_support,urllib2.HTTPHandler)

	pic_num = len(picidlist)
	i = 1
	for pic_id in picidlist:
		url = url_pre + pic_id
		print("total:%d ,curr:%d,id:%s, %s" % (pic_num,i,pic_id,url))
		#download web page
		html = opener.open(url).read()
		#pause html
		soup = BeautifulSoup.BeautifulSoup(html)
		items = soup.findAll(attrs={'class':'j-big-pic twitter_pic'})
		# items = soup.findAll(attrs={'class':'item-pic-origin'})
		#down pic
		pic_path = getPicPath(pic_id)
		for item in items:
			data = urllib2.urlopen(item['src']).read()
			# print("pic src:%s" % item['src'])
			f = open(pic_path,'wb')
			f.write(data)
			f.close()
		i+=1

if __name__ == '__main__':
	if len(sys.argv) == 2 and sys.argv[1]=='-h':
		print("Usage:   mls_cutpic.py [ -h | -v | -fno-download ]")
	elif len(sys.argv) == 2 and sys.argv[1]=='-v':
		print("mlscp version 0.1 by pgdnxu [pgdninf@gmail.com]")
	else:
		pic_id_list = getPicIds('./pic_ids.txt')

		if len(sys.argv) == 2 and sys.argv[1]=='-fno-download':
			procPics(pic_id_list)
		elif len(sys.argv) == 1:
			downPics(pic_id_list)
			procPics(pic_id_list)
		else:
			print("Usage:   mls_cutpic.py [ -h | -v | -fno-download ]")
