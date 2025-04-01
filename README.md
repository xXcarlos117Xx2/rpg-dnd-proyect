# 🧙 RPG DnD Web App (React + Flask + Cloudinary)

Un proyecto fullstack moderno para gestionar personajes de rol narrativo estilo D&D. Esta aplicación permite crear, visualizar y administrar personajes, hechizos, inventario e imágenes asociadas, con un backend en Flask y un frontend moderno en React (Vite).

---

## 🧰 Tecnologías utilizadas

### 🔹 Frontend
- [React 18+](https://react.dev/)
- [Vite](https://vitejs.dev/) para desarrollo ultra rápido
- [React Router DOM v6+](https://reactrouter.com/en/main)
- [Axios](https://axios-http.com/) para llamadas HTTP

### 🔹 Backend
- [Flask](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Migrate](https://flask-migrate.readthedocs.io/)
- [Flask-CORS](https://flask-cors.readthedocs.io/)
- [Cloudinary](https://cloudinary.com/) para almacenamiento de imágenes
- [Pipenv](https://pipenv.pypa.io/) para gestión de entorno

---

## 📁 Estructura de carpetas

```
rpg-dnd-proyect/
├── front/                   # Frontend React (Vite)
│   ├── pages/               # Vistas principales
│   ├── components/          # Reutilizables
│   ├── Layout.jsx           # Diseño base (navegación)
│   ├── routes.jsx           # Enrutador principal
│   ├── main.jsx             # Entrada de React
│   └── ...
├── back/                    # Backend Flask
│   ├── app/
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── config.py
│   │   └── __init__.py
│   ├── run.py
│   ├── requirements.txt
│   ├── .env
│   └── Pipfile
```

---

## 🚀 Instalación

### 🧩 Requisitos

- Python 3.11+
- Node.js 18+
- Pipenv

---

### 🔧 Backend (Flask)

```bash
cd back
pipenv install
pipenv run install       # Instala requirements.txt
pipenv run initdb        # Inicializa migraciones
pipenv run migrate       # Genera esquema inicial
pipenv run upgrade       # Aplica la base de datos
pipenv run start         # Ejecuta el servidor Flask (http://localhost:5000)
```

> Recuerda configurar tu archivo `.env` con tus credenciales de Cloudinary:
> 
> ```env
> CLOUDINARY_CLOUD_NAME=tu_nombre
> CLOUDINARY_API_KEY=tu_api_key
> CLOUDINARY_API_SECRET=tu_api_secret
> ```

---

### ⚛️ Frontend (React)

```bash
cd front
npm install
npm run dev
```

> El frontend corre por defecto en `http://localhost:5173`

---

## 🧪 API disponible (desde Flask)

| Método | Ruta              | Descripción                  |
|--------|-------------------|------------------------------|
| GET    | `/api/ping`       | Test del servidor            |
| POST   | `/api/characters` | Crear personaje |
| GET    | `/api/characters` | Listar personajes |
| POST   | `/api/upload`     | Subida a Cloudinary |

---

## 🗺️ Enrutamiento en React

| Ruta             | Componente         | Descripción                    |
|------------------|--------------------|--------------------------------|
| `/`              | `Home`             | Página de inicio               |

---

## 📌 Estado actual

✅ Backend funcional (Flask + SQLite + Cloudinary)  
✅ Frontend React (con rutas modernas y layout base)  
🚧 CRUD de personajes en desarrollo  
🚧 Subida de imágenes vía Cloudinary  
🚧 Panel de administración y fichas individuales  

---

## 💡 Próximos pasos

- Crear endpoint `POST /characters`
- Llamar desde React con Axios
- Mostrar personajes en lista o cards
- Subida de imágenes (retrato de personaje, objetos, hechizos)
- Agregar sistema de condiciones/estados

---

## 🧙 Autor

Proyecto de desarrollo narrativo interactivo basado en partidas de D&D adaptadas para la web.  
Por: **@xXcarlos117Xx2** ✨  