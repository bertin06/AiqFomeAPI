from django.views import View
from django.http import JsonResponse, HttpResponse
from .aiqfome import Aiq
import xml.etree.ElementTree as ET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class GetData(View):

    def get(self, request, *args, **kwargs):
        aiq = Aiq()
        is_xml = self.request.GET.get('xml', '')
        data = self.request.session.get('token-data', False)
        if data:
            aiq.set_data(data)
        else:
            aiq.new()
            self.request.session['token-data'] = aiq.get_data()
        self.response = aiq.get_orders(self.request.GET.get('start', ''), self.request.GET.get('end', ''))
        if aiq.error:
            if is_xml.lower() == 'true':
                root = ET.Element("root")
                self.build_xml(root, self.response)
                xml_string = ET.tostring(root, encoding='unicode')
                return HttpResponse(xml_string, content_type="application/xml", status = self.response.get('code'))
            else:
                return JsonResponse(self.response, status = self.response.get('code'))
        else:
            if is_xml.lower() == 'true':
                root = ET.Element("root")
                self.build_xml(root, self.response)
                xml_string = ET.tostring(root, encoding='unicode')
                return HttpResponse(xml_string, content_type="application/xml")
            else:
                return JsonResponse(self.response)

    def build_xml(self, parent: ET.Element, data):
        if isinstance(data, dict):
            for key, value in data.items():
                subelement = ET.SubElement(parent, key)
                self.build_xml(subelement, value)
        elif isinstance(data, list):
            for item in data:
                item_element = ET.SubElement(parent, 'item')
                self.build_xml(item_element, item)
        else:
            parent.text = str(data)

@method_decorator(csrf_exempt, name='dispatch')
class NewOrder(View):

    def post(self, request, *args, **kwargs):
        aiq = Aiq()
        is_xml = self.request.POST.get('xml', '')
        body = self.request.POST.get('body', '')
        data = self.request.session.get('token-data', False)
        if data:
            aiq.set_data(data)
        else:
            aiq.new()
            self.request.session['token-data'] = aiq.get_data()
        self.response = aiq.new_order(body)
        if aiq.error:
            if is_xml.lower() == 'true':
                root = ET.Element("root")
                self.build_xml(root, self.response)
                xml_string = ET.tostring(root, encoding='unicode')
                return HttpResponse(xml_string, content_type="application/xml", status = self.response.get('code'))
            else:
                return JsonResponse(self.response, status = self.response.get('code'))
        else:
            if is_xml.lower() == 'true':
                root = ET.Element("root")
                self.build_xml(root, self.response)
                xml_string = ET.tostring(root, encoding='unicode')
                return HttpResponse(xml_string, content_type="application/xml")
            else:
                return JsonResponse(self.response)

    def build_xml(self, parent: ET.Element, data):
        if isinstance(data, dict):
            for key, value in data.items():
                subelement = ET.SubElement(parent, key)
                self.build_xml(subelement, value)
        elif isinstance(data, list):
            for item in data:
                item_element = ET.SubElement(parent, 'item')
                self.build_xml(item_element, item)
        else:
            parent.text = str(data)