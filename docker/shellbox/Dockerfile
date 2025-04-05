FROM ubuntu:noble

EXPOSE 4200

RUN ["apt", "update"]
RUN ["apt", "upgrade", "-y"]
RUN ["apt", "install", "shellinabox", "util-linux", "-y"]

COPY ./changePwAndStartService.sh /startup.sh 

# CMD ["/usr/bin/shellinaboxd", "-t", "--css", "/etc/shellinabox/options-enabled/00_White On Black.css"]
CMD ["/bin/bash", "/startup.sh"]