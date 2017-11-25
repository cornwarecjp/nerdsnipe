#!/usr/bin/env python
#    botg.py
#    Copyright (C) 2015 by CJP
#
#    This file is part of Amiko Pay.
#
#    Amiko Pay is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Amiko Pay is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Amiko Pay. If not, see <http://www.gnu.org/licenses/>.
#
#    Additional permission under GNU GPL version 3 section 7
#
#    If you modify this Program, or any covered work, by linking or combining it
#    with the OpenSSL library (or a modified version of that library),
#    containing parts covered by the terms of the OpenSSL License and the SSLeay
#    License, the licensors of this Program grant you additional permission to
#    convey the resulting work. Corresponding Source for a non-source form of
#    such a combination shall include the source code for the parts of the
#    OpenSSL library used as well as that of the covered work.

import binascii
import decimal
import sys

from crypto import Key, SHA256, RIPEMD160
import base58
import bitcointransaction as btx



mBTC = 100000 #Satoshi


def readPrivateKey(filename):
	with open(filename, "rb") as f:
		privateKey = f.read()
	privateKey = privateKey.split("\n")[0] #first line
	privateKey = privateKey.strip() #ignore whitespace
	return base58.decodeBase58Check(privateKey, 128) #PRIVKEY = 128


def getAddress(key):
	publicKeyHash = RIPEMD160(SHA256(key.getPublicKey()))
	return base58.encodeBase58Check(publicKeyHash, 0) #PUBKEY_ADDRESS = 0


def makekey(args):
	with open(args[0], 'rb') as f:
		data = f.read()

	privateKey = SHA256(data)

	k = Key()
	k.setPrivateKey(privateKey)

	privateKey = base58.encodeBase58Check(privateKey, 128) #PRIVKEY = 128

	address = getAddress(k)

	with open(address, "wb") as f:
		f.write(privateKey + "\n")
	print "Saved as ", address


def hash160(args):
	with open(args[0], 'rb') as f:
		data = f.read().strip()

	h = RIPEMD160(SHA256(data))
	print base58.encodeBase58Check(h, 0) #PUBKEY_ADDRESS = 0


def getinfo(args):
	for filename in args:
		print "----------------"
		print "Filename: ", filename
		privateKey = readPrivateKey(filename)
		k = Key()
		k.setPrivateKey(privateKey)
		print "Public key: ", k.getPublicKey().encode("hex")
		print "Address: ", getAddress(k)


def toScript(args):
	#Load the keys
	keys = []
	for filename in args:
		privateKey = readPrivateKey(filename)
		k = Key()
		k.setPrivateKey(privateKey)
		keys.append(k)

	def getKey(question):
		for i in range(len(keys)):
			print i+1, getAddress(keys[i])
		i = int(raw_input(question)) - 1
		return keys[i]

	#Ask for input information:
	inputs = []
	totalAmount = 0
	while True:
		txid = raw_input("Transaction ID of unspent output (Enter to stop): ")
		txid = txid.strip()
		if txid == "":
			break
		txid = binascii.unhexlify(txid)[::-1]

		vout = int(raw_input("Output index of unspent output: "))
		k = getKey("Address of unspent output: ")
		inputs.append((txid, vout, k))

		totalAmount += int(decimal.Decimal(
			raw_input("Amount in unspent output (mBTC): ")
			) * mBTC)

	print "Total of amounts: %s mBTC" % str(decimal.Decimal(totalAmount)/mBTC)

	fee = int(0.6 * mBTC)
	print "Transaction fee is set to: %s mBTC" % str(decimal.Decimal(fee)/mBTC)

	
	destAddress = raw_input("Destination address: ")
	destAddressHash = base58.decodeBase58Check(destAddress, 0) #PUBKEY_ADDRESS = 0
	destPreimg = raw_input("Destination hash pre-image: ").strip()
	destHash = RIPEMD160(SHA256(destPreimg))

	print "Script: OP_HASH160 %s OP_EQUALVERIFY OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG" % \
		(base58.encodeBase58Check(destHash, 0), destAddress)

	destData = raw_input("Data to add: ")

	tx = btx.Transaction(
		tx_in = [
			btx.TxIn(x[0], x[1])
			for x in inputs
			],
		tx_out = [
			btx.TxOut(totalAmount - fee, btx.Script.P2SHPubKey(
				btx.Script.hashPubKey(destHash, destAddressHash)
				)),
			btx.TxOut(0, btx.Script.dataPubKey(destData))
			]
		)

	for i in range(len(inputs)):
		#print tx.tx_in[i].previousOutputHash.encode("hex"), tx.tx_in[i].previousOutputIndex
		key = inputs[i][2]
		address = getAddress(key)
		hash = base58.decodeBase58Check(address, 0) #PUBKEY_ADDRESS = 0
		scriptPubKey = btx.Script.standardPubKey(hash)
		tx.signInput(i, scriptPubKey, [None, key.getPublicKey()], [key])

	serialized = tx.serialize()
	print "%d bytes" % len(serialized)
	print "%f mBTC/kB" % ((float(fee)/mBTC) / (len(serialized)/1024.0))
	print "Serialized transaction:"
	print serialized.encode("hex")
	print "Transaction ID:", tx.getTransactionID()[::-1].encode("hex")


def fromScript(args):
	#Load the key
	privateKey = readPrivateKey(args[0])
	key = Key()
	key.setPrivateKey(privateKey)

	#Ask for input information:
	txid = raw_input("Transaction ID of unspent output: ")
	txid = txid.strip()
	txid = binascii.unhexlify(txid)[::-1]

	totalAmount = int(decimal.Decimal(
		raw_input("Amount in unspent output (mBTC): ")
		) * mBTC)

	destPreimg = raw_input("Input hash pre-image: ")
	destHash = RIPEMD160(SHA256(destPreimg))

	fee = int(0.6 * mBTC)
	print "Transaction fee is set to: %s mBTC" % str(decimal.Decimal(fee)/mBTC)
	
	destAddress = raw_input("Destination address: ")
	destAddressHash = base58.decodeBase58Check(destAddress, 0) #PUBKEY_ADDRESS = 0

	tx = btx.Transaction(
		tx_in = [
			btx.TxIn(txid, 0)
			],
		tx_out = [
			btx.TxOut(totalAmount - fee, btx.Script.standardPubKey(destAddressHash))
			]
		)

	sourceAddress = getAddress(key)
	sourceAddressHash = base58.decodeBase58Check(sourceAddress, 0) #PUBKEY_ADDRESS = 0
	innerPubKey = btx.Script.hashPubKey(destHash, sourceAddressHash)
	#scriptPubKey = btx.Script.P2SHPubKey(innerPubKey)
	tx.signInput(0, innerPubKey, [None, key.getPublicKey(), destPreimg, innerPubKey.serialize()], [key])

	serialized = tx.serialize()
	print "%d bytes" % len(serialized)
	print "%f mBTC/kB" % ((float(fee)/mBTC) / (len(serialized)/1024.0))
	print "Serialized transaction:"
	print serialized.encode("hex")
	print "Transaction ID:", tx.getTransactionID()[::-1].encode("hex")



funcs = \
{
"makekey": makekey,
"hash160": hash160,
"getinfo": getinfo,
"toScript": toScript,
"fromScript": fromScript
}
funcNames = funcs.keys()
funcNames.sort()

if len(sys.argv) < 2 or sys.argv[1] not in funcNames:
	print "Usage: %s <command> [<args>]" % sys.argv[0]
	print "Command can be one of:"
	for fn in funcNames:
		print fn
	sys.exit(1)

funcs[sys.argv[1]](sys.argv[2:])

