FROM ghcr.io/geode-solutions/vtk:3.9-cpu

WORKDIR /app

COPY . .
RUN pip3 install --user -r requirements.txt && pip3 cache purge
ENV PYTHONPATH="/usr/local:$PYTHONPATH"

CMD python vtkw_server.py

EXPOSE 1234