# Sbily

[![license mit](https://img.shields.io/badge/licence-MIT-blue)](/LICENSE)

A Django project for a link shortener.

## Technologies used

- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [Docker](https://www.docker.com/)

## How to execute the project

To run the project you need to have [Python](https://www.python.org/), [Node](https://nodejs.org/) (To run TailwindCSS) and [Git](https://git-scm.com) installed on your machine or just use [Docker](#9-running-with-docker) together with [Git](https://git-scm.com).

### 1. Clone this repository

```bash
git clone https://github.com/dkshs/sbily.git
```

### 2. Access the project folder

```bash
cd sbily
```

### 3. Virtual environment

Start a virtual environment and activate it. If you don't know how, this might help: <https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments>.

### 4. Install dependencies

Python dependencies:

```bash
pip install -r requirements/local.txt
```

Node dependencies:

```bash
npm install
```

### 5. Configure environment variables

Copy the `.env.example` file in this directory to `.env` _(which will be ignored by Git)_:

```bash
cp .env.example .env
```

Then define each variable in `.env`:

```env
SECRET_KEY=Enter_A_Secret_Password_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
BASE_URL=http://127.0.0.1:8000/
```

### 6. Make the migrations

```bash
python manage.py migrate
```

### 7. Create a super user

```bash
python manage.py createsuperuser
```

### 8. Running application in development mode

Django application:

```bash
python manage.py runserver
```

Tailwind css:

```bash
npm run dev
```

- The application will start locally - go to: <http://127.0.0.1:8000/>

- In the administrative area, enter the username and password created in [step 7](#7-create-a-super-user).

### 9. Running with Docker

Having the [source code](#1-clone-this-repository) with the [variables defined](#5-configure-environment-variables), with [Docker](https://www.docker.com/) installed, let's up the container:

```bash
docker compose up -d
```

_When started, the container starts the Django application!_

> **_The steps below will only be necessary if you have not yet carried out the migrations and created a super user! If you have already done so, the application can be accessed at: <http://localhost:8080>_**

You will need to enter the container via CLI:

```bash
docker compose exec -it app zsh
```

> Now you are inside the container!

You will need to make the migrations:

```bash
python manage.py migrate
```

Creating a super user:

```bash
python manage.py createsuperuser
```

- The application is running on: <http://localhost:8080/>.

## License

This project is under the [MIT license](/LICENSE).

🔝[Back to top](#sbily)
