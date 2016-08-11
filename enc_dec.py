#!/usr/bin/env python

"""Encrypts and Decrypts the given files with AES and encodes with base64"""


__author__ = "Vamsi Krishna Konakalla, Rinku Sharma, Varun Vijay, Ram Kishore"
__copyright__ = "SAAS QA Standard"
__credits__ = ["-"]
__license__ = "BSD"
__version__ = "0.0.1"
__maintainer__ = "Vamsi Krishna Konakalla"
__email__ = "vamsi.krishna.konakalla@oracle.com"
__status__ = "POC"

from Crypto.Cipher import AES
from tempfile import mkstemp
from shutil import move
from os import remove, close
from optparse import OptionParser
import base64
import json
import random
import string


#Useful Utils
def JSONFileReader(path):
	return json.loads(open(path).read())
	
def generate_Randomchars(N=32):
	return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
	
def read_file_properties(path="enc.json"):
	file_content = JSONFileReader(path)
	return file_content.get('filepaths_keys',{})
	
	
def fetch_processed_line(line,keylist):
	if not line:
		return line + "\n"
	if  (line.split('=',1)[0] in keylist or (len(keylist)==1 and 'ALL' in keylist)) and (len(line.split("=",1)) >1):
		return line.split('=',1)[0] + '=' + Translator().encode_AES(line.split('=',1)[1]) + "\n"
	else:
		return line + "\n"
		

class Translator(object):

	def __init__(self,*args,**kwargs):
		self.secret = kwargs.get('secret','DMENYZEMZBDARJVK9RHLBN3MEIU9V3D5')
		self.cipher = AES.new(self.secret)
		# the character used for padding--with a block cipher such as AES, the value
		# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
		# used to ensure that your value is always a multiple of BLOCK_SIZE
		self.PADDING = '{'
		self.BLOCK_SIZE = kwargs.get('block_size',32)
		self.pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING
		
	def encode_AES(self,to_enc):
		EncodeAES = lambda c, s: base64.b64encode(c.encrypt(self.pad(s)))
		return EncodeAES(self.cipher,to_enc)
		
	def decode_AES(self,to_dec):
		DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.PADDING)
		return DecodeAES(self.cipher,to_dec)
		
class EncodeSelected(object):
	def __init__(self,*args,**kwargs):
		self.files_meta_list = kwargs.get('file_info_dict',read_file_properties())
	
	def encrypt_file(self,file_path,keylist):
		#Create temp file
		fh, abs_path = mkstemp()
		with open(abs_path,'w') as new_file:
			with open(file_path) as old_file:
				for line in old_file:
					tmp_line = fetch_processed_line(line,keylist)
					new_file.write(tmp_line)
		close(fh)
		#Remove original file
		remove(file_path)
		#Move new file
		move(abs_path, file_path)
	
	def encrypt_file_wrapper(self):
		for fileinfo in self.files_meta_list:
			self.encrypt_file(fileinfo.get('filepath'),fileinfo.get('keys'))
	
		

		
if __name__ == "__main__":
	#print Translator().encode_AES('password')
	#print Translator().decode_AES(Translator().encode_AES('password'))
	#print read_file_properties()
	#EncodeSelected().encrypt_file_wrapper()
	parser = OptionParser(usage="usage: %prog [options] filename",
                          version="%prog 0.1")
	parser.add_option("-e", "--encode",
                      dest="str_encode",
                      help="Encode Given string")
	parser.add_option("-d", "--decode",
                      dest="str_decode",
                      help="Decode Given string")
	parser.add_option("-f", "--forceencodeconfig",action="store_true",
                      dest="str_encode_config",
					  default =False,
                      help="Encode Files in config")
	(options, args) = parser.parse_args()	
	if options.str_encode:
		print Translator().encode_AES(options.str_encode)
	if options.str_decode:
		print Translator().decode_AES(options.str_decode)
	if options.str_encode_config:
		EncodeSelected().encrypt_file_wrapper()
