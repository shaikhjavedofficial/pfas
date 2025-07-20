# pfas

1. To Start the docker build and container:

    docker-compose up --build --scale backend=1 -d

2. To chekc the scaling logs

   docker-compose logs -f autoscaler
3. To stop and remove

   docker-compose down -v --remove-orphans
4.
