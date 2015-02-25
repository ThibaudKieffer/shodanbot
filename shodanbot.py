#!/usr/bin/env python2
# -*- coding: utf8 -*-
import irclib
import ircbot
import shodan
import sys
import time
import re

API_KEY = "ENTER HERE YOUR API KEY"

class BotShodan(ircbot.SingleServerIRCBot):
    def __init__(self):
        
        #Parameters are : IRC server, port, bot name and real name.
        ircbot.SingleServerIRCBot.__init__(self, [("irc.rizon.net", 6667)],
                                           "shodan", "Bot made to consults Shodan")
        self.search = "?search"
        self.informations = "?informations"
        self.manuel = "?man"
        self.requestnb="?resultnumber"
        # Setup the API
        self.api = shodan.Shodan(API_KEY)
        self.nb = 0
        self.request_nb=5
        
    def on_welcome(self, serv, ev):
        serv.join("#channel")

    def on_pubmsg(self, serv, ev):
        auteur = irclib.nm_to_n(ev.source())
        canal = ev.target()
        message = ev.arguments()[0].lower()
        if self.search in message:
            try:
                self.nb=0
                query = message.replace('?search ','')
                nb_result = self.api.count(query)
            
                serv.privmsg(canal,'Number of result(s) : %s' % (nb_result.get('total')))

                result = self.api.search(query)
                
                for service in result['matches']:
                    if (self.nb < self.request_nb):
                        serv.privmsg(canal, service['ip_str'])
                        time.sleep(0.1)
                        self.nb=self.nb+1
                    else:
                        self.nb=0
                        break
                        
            except Exception, e:
                serv.privmsg(canal, "This request don't work.")
                
        if self.informations in message:
            try:
                query = message.replace('?informations','')
                query = query.replace(' ','')
        
                host = self.api.host(query)
                serv.privmsg(canal, "IP: %s" % (host['ip_str']))
                serv.privmsg(canal, "Organization: %s" % (host.get('org', 'n/a')))
                serv.privmsg(canal, "Operating System: %s" % (host.get('os', 'n/a')))
                serv.privmsg(canal, "country: %s" % (host.get('country_name')))
                serv.privmsg(canal, "city: %s" % (host.get('city')))
                serv.privmsg(canal, "longitude: %s" % (host.get('longitude')))
                serv.privmsg(canal, "latitude: %s" % (host.get('latitude')))
                for item in host['data']:
                    serv.privmsg(canal, "Port: %s" % (item['port']))
                    serv.privmsg(canal, "Banner: %s" % (item['data']))

            except Exception, e:
                serv.privmsg(canal, "Information(s) not available.")

        if self.manuel in message:
            serv.privmsg(canal, "**** User manual ****")
            serv.privmsg(canal, "?search : make a Shodan request")
            serv.privmsg(canal, "ex : ?search netcam")
            serv.privmsg(canal, "?resultnumber : define the number of showed results")
            serv.privmsg(canal, "ex : ?resultnumber 10")
            serv.privmsg(canal, "?informations : give IP informations")
            serv.privmsg(canal, "ex : ?informations 176.31.245.104") 

        if self.requestnb in message:
            query = message.replace('?resultnumber ','')
            try:
                self.request_nb = int(query)
                serv.privmsg(canal, "The number of showed result(s) is already %d" % (self.request_nb))

            except Exception, e:
                serv.privmsg(canal, "You entered a wrong data.")

if __name__ == "__main__":
    BotShodan().start()
