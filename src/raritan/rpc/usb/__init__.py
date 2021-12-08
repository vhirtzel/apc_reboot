# SPDX-License-Identifier: BSD-3-Clause
#
# Copyright 2020 Raritan Inc. All rights reserved.
#
# This is an auto-generated file.

#
# Section generated by IdlC from "Usb.idl"
#

import raritan.rpc
from raritan.rpc import Interface, Structure, ValueObject, Enumeration, typecheck, DecodeException
import raritan.rpc.event

import raritan.rpc.usb


# structure
class UsbDevice(Structure):
    idlType = "usb.UsbDevice:1.0.0"
    elements = ["bus", "device", "vendorId", "productId"]

    def __init__(self, bus, device, vendorId, productId):
        typecheck.is_int(bus, AssertionError)
        typecheck.is_int(device, AssertionError)
        typecheck.is_int(vendorId, AssertionError)
        typecheck.is_int(productId, AssertionError)

        self.bus = bus
        self.device = device
        self.vendorId = vendorId
        self.productId = productId

    @classmethod
    def decode(cls, json, agent):
        obj = cls(
            bus = json['bus'],
            device = json['device'],
            vendorId = json['vendorId'],
            productId = json['productId'],
        )
        return obj

    def encode(self):
        json = {}
        json['bus'] = self.bus
        json['device'] = self.device
        json['vendorId'] = self.vendorId
        json['productId'] = self.productId
        return json

# interface
class Usb(Interface):
    idlType = "usb.Usb:1.0.2"

    # structure
    class Settings(Structure):
        idlType = "usb.Usb_1_0_2.Settings:1.0.0"
        elements = ["hostPortsEnabled"]

        def __init__(self, hostPortsEnabled):
            typecheck.is_bool(hostPortsEnabled, AssertionError)

            self.hostPortsEnabled = hostPortsEnabled

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                hostPortsEnabled = json['hostPortsEnabled'],
            )
            return obj

        def encode(self):
            json = {}
            json['hostPortsEnabled'] = self.hostPortsEnabled
            return json

    # value object
    class SettingsChangedEvent(raritan.rpc.event.UserEvent):
        idlType = "usb.Usb_1_0_2.SettingsChangedEvent:1.0.0"

        def __init__(self, oldSettings, newSettings, actUserName, actIpAddr, source):
            super(raritan.rpc.usb.Usb.SettingsChangedEvent, self).__init__(actUserName, actIpAddr, source)
            typecheck.is_struct(oldSettings, raritan.rpc.usb.Usb.Settings, AssertionError)
            typecheck.is_struct(newSettings, raritan.rpc.usb.Usb.Settings, AssertionError)

            self.oldSettings = oldSettings
            self.newSettings = newSettings

        def encode(self):
            json = super(raritan.rpc.usb.Usb.SettingsChangedEvent, self).encode()
            json['oldSettings'] = raritan.rpc.usb.Usb.Settings.encode(self.oldSettings)
            json['newSettings'] = raritan.rpc.usb.Usb.Settings.encode(self.newSettings)
            return json

        @classmethod
        def decode(cls, json, agent):
            obj = cls(
                oldSettings = raritan.rpc.usb.Usb.Settings.decode(json['oldSettings'], agent),
                newSettings = raritan.rpc.usb.Usb.Settings.decode(json['newSettings'], agent),
                # for event.UserEvent
                actUserName = json['actUserName'],
                actIpAddr = json['actIpAddr'],
                # for idl.Event
                source = Interface.decode(json['source'], agent),
            )
            return obj

        def listElements(self):
            elements = ["oldSettings", "newSettings"]
            elements = elements + super(raritan.rpc.usb.Usb.SettingsChangedEvent, self).listElements()
            return elements

    class _getSettings(Interface.Method):
        name = 'getSettings'

        @staticmethod
        def encode():
            args = {}
            return args

        @staticmethod
        def decode(rsp, agent):
            _ret_ = raritan.rpc.usb.Usb.Settings.decode(rsp['_ret_'], agent)
            typecheck.is_struct(_ret_, raritan.rpc.usb.Usb.Settings, DecodeException)
            return _ret_

    class _setSettings(Interface.Method):
        name = 'setSettings'

        @staticmethod
        def encode(settings):
            typecheck.is_struct(settings, raritan.rpc.usb.Usb.Settings, AssertionError)
            args = {}
            args['settings'] = raritan.rpc.usb.Usb.Settings.encode(settings)
            return args

        @staticmethod
        def decode(rsp, agent):
            _ret_ = rsp['_ret_']
            typecheck.is_int(_ret_, DecodeException)
            return _ret_

    class _getDevices(Interface.Method):
        name = 'getDevices'

        @staticmethod
        def encode():
            args = {}
            return args

        @staticmethod
        def decode(rsp, agent):
            usbDevices = [raritan.rpc.usb.UsbDevice.decode(x0, agent) for x0 in rsp['usbDevices']]
            for x0 in usbDevices:
                typecheck.is_struct(x0, raritan.rpc.usb.UsbDevice, DecodeException)
            return usbDevices
    def __init__(self, target, agent):
        super(Usb, self).__init__(target, agent)
        self.getSettings = Usb._getSettings(self)
        self.setSettings = Usb._setSettings(self)
        self.getDevices = Usb._getDevices(self)