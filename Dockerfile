#Deriving the latest base image
FROM python:3

ENV DB_HOST='localhost'
ENV DB_NAME='scaper_db'
ENV DB_PORT=5432
ENV DB_USER_NAME='postgres'
ENV DB_USER_PASSWORD='postgres'
ENV SCRAPEOPS_API_KEY='6a96635c-b6ac-4bd6-9272-5dcb62a7f9ba'
ENV SCRAPEOPS_HEADER_URL='http://headers.scrapeops.io/v1/browser-headers?api_key='
ENV SCRAPEOPS_PROXY_URL='https://proxy.scrapeops.io/v1/?'
ENV JOBS_URL='https://www.indeed.com/jobs?'
ENV JOBS_ID_URL='https://www.indeed.com/m/basecamp/viewjob?viewtype=embedded&jk='
ENV CSV_LOCATION='data/export_dataframe.csv'

#Run the dependency to the container
ADD requirements.txt /

#Run the underlying requirements
RUN pip install -r requirements.txt

ADD index.py /
ADD send_email.py /
ADD main.py /

#CMD instruction should be used to run the software
#contained by your image, along with any arguments.
CMD [ "python3", "./main.py" ]