from rest_framework import viewsets
from .models import Data
from .serializers import DataSerializer

from django.shortcuts import get_object_or_404
from django.http import Http404
import json
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from django.http import HttpResponse
import os
import cv2 as cv
import math
import time
import numpy as np

from filemanager.east_detection_model import east_detection, decodeBoundingBoxes


def canvas_image_url_multifiles(request, multiple_image_url):
    image_url_multiple = multiple_image_url
    return render(request, "filemanager/templates/canvas_modify_multifiles.html", {"image_url_multiple": json.dumps(image_url_multiple), })

#  the EAST detection algorithm
def east_detect(request):
    data_str = request.body.decode()
    data = json.loads(data_str)
    image_path = data['image_filepath']
    image_path = "." + image_path
    vertices_list = east_detection(image_path)
    results = ""
    for i in range(len(vertices_list)):
        vertices = vertices_list[i]
        for i1 in range(4):
          x1 = int(vertices[i1][0])
          y1 = int(vertices[i1][1])
          x1 = str(x1)
          y1 = str(y1)

          if (i1 == 0):
              results = results + x1 + "$$&" + y1
          else:
              results = results + "$$&" + x1 + "$$&" + y1
        if (i != len(vertices_list) - 1):
              results = results + "***"

    return HttpResponse(json.dumps({"file_content": results}, ensure_ascii=False),
                        content_type="application/json,charset=utf-8")


class DataViewSet(viewsets.ModelViewSet):
    queryset = Data.objects.all()
    serializer_class = DataSerializer

    permission_classes = (permissions.AllowAny,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        serializer = DataSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            for k, v in kwargs.items():
                for id in v.split(','):
                    obj = get_object_or_404(Data, pk=int(id))
                    self.perform_destroy(obj)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)
