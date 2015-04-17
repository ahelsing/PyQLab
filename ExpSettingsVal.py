'''
ExpSettingsValidator

Created on April 17, 2015

Original Author: Brian Donovan

Copyright 2015 Raytheon BBN Technologies

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import h5py
import Libraries
import QGL.Channels

channels = None
instruments = None
measurements = None
sweeps = None


channels = Libraries.channelLib.channelDict
instruments = Libraries.instrumentLib.instrDict
measurements = Libraries.measLib.filterDict
sweeps = Libraries.sweepLib.sweepDict


def is_logicalmarker_channel(name):
	return is_channel_type(name, QGL.Channels.LogicalMarkerChannel)	

def is_physicalmarker_channel(name):
	return is_channel_type(name, QGL.Channels.PhysicalMarkerChannel)	

def is_qubit_channel(name):
	return is_channel_type(name, QGL.Channels.Qubit)	

def is_measurement_channel(name):
	return is_channel_type(name, QGL.Channels.Measurement)	

def requires_physical_channel(name):
	return (is_channel_type(name, QGL.Channels.Qubit) or
	        is_channel_type(name, QGL.Channels.LogicalMarkerChannel) or
	        is_channel_type(name, QGL.Channels.Measurement))

def is_channel_type(name, channelType):
	channels = Libraries.channelLib.channelDict
	return isinstance(channels[name], channelType)	

def test_logical_channels():
	errors = []
	channels = Libraries.channelLib.channelDict
	logicalChannels = [channelName for channelName in channels.keys() if is_logicalmarker_channel(channelName)]
	
	for channel in logicalChannels:
		if not is_logicalmarker_channel(channel):
			continue
		errorHeader = 'LogicalMarkerChannel "{0}" requires a Physical Marker Channel'.format(channel)
		if channels[channel].physChan is not None:
			physicalChannelName = channels[channel].physChan.label
			if physicalChannelName not in channels.keys():
				print errorHeader
				print '\tPhysical Channel "{0}" not found'.format(physicalChannelName)
				errors.append(physicalChannelName)
			elif not is_physicalmarker_channel(physicalChannelName):
				print channels[channel].physChan
				print '\tChannel "{0}" is not a Physical Marker Channel'.format(physicalChannelName)
				errors.append(physicalChannelName)
	return errors

def test_physical_channels():
	errors = []
	channels = Libraries.channelLib.channelDict
	physicalChannels = [channelName for channelName in channels.keys() if is_physicalmarker_channel(channelName)]

	for channel in physicalChannels:
		awg = channels[channel].AWG.label
		if awg == '':
			print 'Physical Channel "{0}" requires an AWG assignment'.format(channel)
			errors.append(channel)
		elif awg not in instruments.keys():
			print 'Physical Channel "{0}" AWG {1} not found'.format(channel, awg)
			errors.append(channel)

		# test AWG name to channel format
		validName = True
		validName &= '-' in channel
		if validName:
			awgName, awgChan = channel.split('-')
			if awgName not in instruments.keys():
				print 'Physical Channel "{0}" Label format is invalid. It should be Name-Channel'.format(channel)				
				errors.append(channel)
			if awgName != awg:
				print 'Physical Channel "{0}" Label AWGName {1} != AWG.label {2}'.format(channel, awgName, awg)
				errors.append(channel)
		else:
			print 'Physical Channel "{0}" Label format is invalid. It should be Name-Channel'.format(channel)				
			errors.append(channel)

	return errors

def test_require_physical():
	errors = []
	channels = Libraries.channelLib.channelDict
	testChannels = [channelName for channelName in channels.keys() if requires_physical_channel(channelName)]

	for channel in testChannels:
		physicalChannel = channels[channel].physChan
		if physicalChannel is None:
			print '"{0}" channel "{1}" Physical Channel is not defined'.format(channels[channel].__class__.__name__, channel)
			errors.append(channel)

	return errors

def test_measurement_channels():
	errors = []
	channels = Libraries.channelLib.channelDict
	measurementChannels = [channelName for channelName in channels.keys() if is_measurement_channel(channelName)]

	for channel in measurementChannels:
		physicalChannel = channels[channel].physChan
		if physicalChannel is None:
			print 'Measurement channel "{0}" Physical Channel is not defined'.format(channel)
			errors.append(channel)

	return errors	

def lint_channelLib():
	errors = []
	if 'digitizerTrig' not in channels.keys():
		print 'A LogicalMarkerChannel named digitizerTrig is required'
		errors.append('digitizerTrig')
			
	# test gate pulses

	if 'slaveTrig' not in channels.keys():
		print 'A LogicalMarkerChannel named slaveTrig is required'
		errors.append('slaveTrig')		

	# test map_logical_to_physical
	rp_errors = test_require_physical()
	pc_errors = test_physical_channels()
	lc_errors = test_logical_channels()

	if pc_errors != []:
		errors.append(pc_errors)
	if lc_errors != []:		
		errors.append(lc_errors)
	if rp_errors != []:		
		errors.append(rp_errors)		

	print errors
	return errors

def validate_lib():
	if lint_channelLib() != []:
		return False
	return True

def default_repr(items, item):
	return '\t{0}: {1}'.format(item, 
							items[item].__class__.__name__)

def default_list_repr(items, name):
	print 'Listing available {0}:'.format(name)
	for item in items.keys():
		print default_repr(items,item)

def list_channels():
	print 'Listing available channels:'
	for channel in channels.keys():
		print '\t', repr(channels[channel])

def list_instruments():
	default_list_repr(instruments, 'instruments')
	
def list_measurements():
	default_list_repr(measurements, 'measurements')
	
def list_sweeps():
	default_list_repr(sweeps, 'sweeps')
		

def list_config():
	list_channels()
	print
	list_instruments()
	print
	list_measurements()
	print
	list_sweeps()

if __name__ == '__main__':
	list_config()
	validate_lib()
