import falcon
import json
from tado_guestmode import TadoAPI   # NOQA


class AddGuest(object):

    def on_get(self, req, resp):
        """ Creates a guest user but sets guest geolocation to untracked"""
        status, updated, message = tado.addGuest()
        if status:
            status, message = tado.updateGuestLocation()
            response = [{"success": status, "updated": updated, "message": message}]
        else:
            response = [{"success": status, "updated": updated, "message": message}]
        resp.body = json.dumps(response)


class DeleteGuest(object):

    def on_get(self, req, resp):
        """ Deletes a guest user """
        status, message = tado.deleteGuest()
        response = [{"success": status, "message": message}]
        resp.body = json.dumps(response)


class GuestTracking(object):

    def on_get(self, req, resp):
        """ Returns current tracking state of the guest."""
        status, message, geoTracking = tado.getGuestTracking()
        response = [{"success": status, "message": message, "geoTracking": geoTracking}]
        resp.body = json.dumps(response)


class GuestTrackingOn(object):

    def on_get(self, req, resp):
        """ Enables guest geotracking """
        status, message, geoTracking = tado.updateGuestTracking(True)
        response = [{"success": status, "message": message, "geoTracking": geoTracking}]
        resp.body = json.dumps(response)


class GuestTrackingOff(object):

    def on_get(self, req, resp):
        """ Enables guest geotracking """
        status, message, geoTracking = tado.updateGuestTracking(False)
        response = [{"success": status, "message": message, "geoTracking": geoTracking}]
        resp.body = json.dumps(response)


app = falcon.App()

tado = TadoAPI()

addguest_endpoint = AddGuest()
delguest_endpoint = DeleteGuest()
guest_endpoint = GuestTracking()
guestenable_endpoint = GuestTrackingOn()
guestdisable_endpoint = GuestTrackingOff()

app.add_route('/add', addguest_endpoint)
app.add_route('/remove', delguest_endpoint)
app.add_route('/status', guest_endpoint)
app.add_route('/enable', guestenable_endpoint)
app.add_route('/disable', guestdisable_endpoint)
