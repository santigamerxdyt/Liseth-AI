---
type: api-endpoint
status: active
method: POST # GET | POST | PUT | DELETE
path: /api/example
auth_required: true
created: {{date}}
updated: {{date}}
tags:
  - api
  - rest
  - endpoint
verified: false
---

# 🌐 ENDPOINT API: {{title}}

## 📍 Firma HTTP
- **Método:** `POST`
- **Ruta:** `/api/...`
- **Autenticación:** Bearer Token en cabecera `Authorization`.

## 📥 Esquema de Solicitud (Request Body)
```json
{
  "key": "value"
}
```

## 📤 Esquema de Respuesta (Response Body)
```json
{
  "status": "success",
  "data": {}
}
```

## ❌ Códigos de Error Posibles
- `401 Unauthorized`: Token ausente o revocado.
- `403 Forbidden`: Privilegios insuficientes o violación BOLA.
- `422 Unprocessable Entity`: Carga útil malformada.
