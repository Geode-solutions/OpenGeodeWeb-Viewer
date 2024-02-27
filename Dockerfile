FROM ghcr.io/geode-solutions/vtk:3.9-cpu

WORKDIR /app

COPY . .
RUN pip3 install --user -r requirements.txt && pip3 cache purge
ENV PYTHONPATH="/usr/local:$PYTHONPATH"

CMD python src/opengeodeweb_viewer/rpc/schemas/vtkw-server.py --port 1234 --host 0.0.0.0

EXPOSE 1234