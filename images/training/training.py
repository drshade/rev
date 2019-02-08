from __future__ import print_function
import time, sys, os, json, random
import numpy as np
import mxnet as mx
from mxnet import nd, autograd, gluon

import boto3

if __name__ == "__main__":
	train_prefix = "random-games"

	s3 = boto3.resource('s3', region_name='eu-west-1')
	my_bucket = s3.Bucket('reversi-games')
	
	records = []

	for obj in my_bucket.objects.all():
		# Eg: random-games2019/02/05/18/reversi_random_games-2-2019-02-05-18-13-39-5825f13d-7342-4b8a-96a6-4f17a3e64e2a
		if not obj.key.startswith(train_prefix):
			continue
		
		print("Loading file: %s (%d records so far)"%(obj.key, len(records)))
		getresp = obj.get()
		body = getresp['Body'].read()
		for entry in body.split('\n'):
			records.append(entry)

		print(records[0])
		sys.exit(1)


	ctx = mx.gpu() if mx.test_utils.list_gpus() else mx.cpu()
	data_ctx = ctx
	model_ctx = ctx
	print("Using context:", ctx)

