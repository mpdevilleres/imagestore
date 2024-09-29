# Usage
You can access the service via http://3.29.127.29

_NOTE: https was not possible due to the timeline given thus a valid domain was not able to get issued and subsequently the SSL certificate_

## Playing with the codes

- to run the application locally please run as below and open your browser http://localhost:8000
  ```bash
  $ make up-local
  ```

- to run test and linting
  ```bash
  $ uv sync
  $ make checkcodestyle
  $ make test
  ```
# Tasks

- [x] Ability to resize the frames from 200 to 150 columns.
- [x] Ability to store the resized images in a database.
- [x] Ability to request image frames using an API with depth_min and depth_max query parameters.
- [x] Ability to use colormap to generate the frames.
- [x] Python should be the major langauge used.
- [x] Deploy the application in a cloud service.

# Highlights
 
- A simple UI has been added to simplify the process of viewing the frames.
- Standard software practices were applied such has linters, tests, scripting and docker build.
- A document database (MongoDB) was chosen as the database due to the nature of the data given.
- The Application is deployed in a EC2 machine.
- as a cloud native design, an object store support was added, in the current code based, a minio instance is utilize which can be change easily to s3 by changing some environment variables.

# Things I wish I had more time to do

- Authentication layer
- Validation of file upload
- More test specially for failed actions
- Better UI :sweat_smile:
- Github Action for building the image
- Github Action for running CI job such as linting and tests

# Architecture and Stack

- `MongoDB`: is the main database as the image frames fits well as document.
- `Minio`: an object store that has local/self-hosted option and is 100% compatible to s3, allowing a easy to switch vendor.
- `Traefik`: a cloud native loadbalancer.
- `Python`: My Programming language loved by many :nerd_face:
- `FastAPI`: Python Framework for quick and easy API
- `Polars`: a Faster alternative to pandas
