"""
Commercial Contracts & Colombian Legal Templates Service for JARVIS / Liseth.
Generates compliant commercial agreements: Professional Services, Non-Disclosure Agreements (NDA),
Promissory Notes (Pagaré con Carta de Instrucciones), and Project Handover Minutes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("jarvis.legal_contracts")


class LegalContractsService:
    """
    Commercial Legal Engineering Engine for Señor Santiago.
    Drafts legally robust contracts governed by Colombian Commercial and Civil Code.
    """

    def get_supported_templates(self) -> List[Dict[str, str]]:
        return [
            {
                "id": "servicios_profesionales",
                "name": "Contrato de Prestación de Servicios Profesionales",
                "description": "Contrato civil/comercial para consultoría, asesoría gerencial o desarrollo técnico independiente sin relación laboral."
            },
            {
                "id": "nda",
                "name": "Acuerdo de Confidencialidad y No Divulgación (NDA)",
                "description": "Protege secretos comerciales, código, modelos financieros e información confidencial de proyectos."
            },
            {
                "id": "pagare",
                "name": "Pagaré a la Orden y Carta de Instrucciones",
                "description": "Título valor ejecutivo para garantizar el pago de cuentas o financiamiento de consultorías."
            },
            {
                "id": "acta_entrega",
                "name": "Acta de Cierre y Entrega a Satisfacción",
                "description": "Formaliza la entrega final y conformidad de entregables y consultorías realizadas."
            }
        ]

    def generate_contract(
        self,
        template_type: str,
        party_b_name: str,
        party_b_id: str = "900.000.000-1",
        party_a_name: str = "Santiago Huerfano Lopez",
        party_a_id: str = "1.000.000.000",
        amount: float = 2500000.0,
        scope: str = "Asesoría estratégica en administración, valoración financiera y optimización de procesos",
        duration_days: int = 60,
        city: str = "Palmira, Valle del Cauca",
        currency: str = "COP"
    ) -> Dict[str, Any]:
        """Drafts a complete legal contract tailored to the input parameters."""
        contract_id = f"CTO-{datetime.now(timezone.utc).year}-{uuid.uuid4().hex[:6].upper()}"
        today_str = datetime.now(timezone.utc).strftime("%d de %B de %Y")
        t_type = template_type.lower().strip()

        if "nda" in t_type or "confidencialidad" in t_type:
            title = "ACUERDO DE CONFIDENCIALIDAD Y NO DIVULGACIÓN (NDA)"
            body = self._draft_nda(contract_id, party_a_name, party_a_id, party_b_name, party_b_id, city, scope, today_str)
        elif "pagare" in t_type or "titulo" in t_type:
            title = "PAGARÉ A LA ORDEN Y CARTA DE INSTRUCCIONES"
            body = self._draft_pagare(contract_id, party_a_name, party_a_id, party_b_name, party_b_id, amount, currency, city, today_str)
        elif "acta" in t_type or "entrega" in t_type:
            title = "ACTA DE ENTREGA Y LIQUIDACIÓN A SATISFACCIÓN"
            body = self._draft_acta(contract_id, party_a_name, party_b_name, scope, amount, currency, city, today_str)
        else:
            title = "CONTRATO DE PRESTACIÓN DE SERVICIOS PROFESIONALES"
            body = self._draft_servicios(contract_id, party_a_name, party_a_id, party_b_name, party_b_id, amount, currency, scope, duration_days, city, today_str)

        return {
            "id": contract_id,
            "title": title,
            "type": t_type,
            "party_a": party_a_name,
            "party_b": party_b_name,
            "amount": amount,
            "currency": currency,
            "city": city,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "content_markdown": body
        }

    def _draft_servicios(self, cid, pa_name, pa_id, pb_name, pb_id, amount, curr, scope, days, city, date_str) -> str:
        return f"""# {cid}
## CONTRATO DE PRESTACIÓN DE SERVICIOS PROFESIONALES INDEPENDIENTES

Entre los suscritos a saber, de una parte **{pb_name}**, identificado con NIT/C.C. No. **{pb_id}**, quien para los efectos del presente contrato se denominará **EL CONTRATANTE**; y de otra parte **{pa_name}**, mayor de edad, domiciliado en {city}, identificado con C.C. No. **{pa_id}**, actuando en calidad de Administrador de Empresas y Consultor Independiente, quien para los efectos de este acto se denominará **EL CONTRATISTA**, hemos acordado celebrar el presente Contrato de Prestación de Servicios, regido por el Código de Comercio de Colombia y las siguientes cláusulas:

---

### CLÁUSULA PRIMERA: OBJETO DEL CONTRATO
EL CONTRATISTA se obliga para con EL CONTRATANTE a ejecutar con plena autonomía técnica y directiva las siguientes actividades profesionales:
> *{scope}*.

### CLÁUSULA SEGUNDA: VALOR Y FORMA DE PAGO
El valor total acordado por la ejecución de los servicios descritos es la suma de **${amount:,.2f} {curr}**. Dicho valor será cancelado contra presentación de Factura Electrónica Pro-Forma o Cuenta de Cobro, mediante transferencia electrónica interoperable (Bre-B, Nequi o cuenta bancaria) a satisfacción del CONTRATANTE.

### CLÁUSULA TERCERA: PLAZO DE EJECUCIÓN
El término de duración del presente contrato será de **{days} días calendario**, contados a partir de la firma del presente documento.

### CLÁUSULA CUARTA: INDEPENDENCIA Y AUSENCIA DE SUBORDINACIÓN
El presente contrato es de naturaleza civil y comercial. Queda expresamente entendido que no genera vínculo laboral alguno, ni subordinación jurídica entre las partes.

### CLÁUSULA QUINTA: CONFIDENCIALIDAD Y PROPIEDAD INTELECTUAL
Las partes acuerdan que cualquier información técnica, financiera o estratégica revelada durante la ejecución será de estricta reserva. Los derechos patrimoniales sobre los entregables finales corresponderán al CONTRATANTE una vez satisfecho el pago integral.

### CLÁUSULA SEXTA: SOLUCIÓN DE CONTROVERSIAS Y DOMICILIO CONTRACTUAL
Cualquier controversia derivada del presente contrato que no pueda ser resuelta de mutuo acuerdo será sometida a los mecanismos de Conciliación de la Cámara de Comercio del domicilio pactado en **{city}**.

En señal de conformidad y aceptación, se suscribe en {city}, a los {date_str}.

| __________________________________________ | __________________________________________ |
| **EL CONTRATANTE** | **EL CONTRATISTA** |
| {pb_name} | {pa_name} |
| NIT/C.C. {pb_id} | C.C. {pa_id} |
"""

    def _draft_nda(self, cid, pa_name, pa_id, pb_name, pb_id, city, scope, date_str) -> str:
        return f"""# {cid}
## ACUERDO DE CONFIDENCIALIDAD Y NO DIVULGACIÓN (NDA)

En la ciudad de {city}, a los {date_str}, comparecen:
- **LA PARTE REVELADORA**: **{pa_name}**, C.C. {pa_id}.
- **LA PARTE RECEPTORA**: **{pb_name}**, NIT/C.C. {pb_id}.

### 1. INFORMACIÓN CONFIDENCIAL OBJETO DE PROTECCIÓN
Se considera Información Confidencial toda información técnica, financiera, algoritmos, modelos de negocio, flujos de caja y metodologías relacionadas con: *{scope}*.

### 2. OBLIGACIONES DE LA PARTE RECEPTORA
La Parte Receptora se compromete a:
- Mantener estricta reserva y no divulgar la información a terceros sin consentimiento previo y por escrito.
- Utilizar la información única y exclusivamente para los fines de evaluación y colaboración comercial.
- Adoptar medidas de seguridad idénticas a las empleadas para custodiar sus propios secretos comerciales.

### 3. VIGENCIA DE LA CONFIDENCIALIDAD
El deber de reserva pactado en este instrumento permanecerá vigente durante un período de **tres (3) años** a partir de la fecha de suscripción.

| **PARTE REVELADORA** | **PARTE RECEPTORA** |
| :--- | :--- |
| {pa_name} (C.C. {pa_id}) | {pb_name} (NIT/C.C. {pb_id}) |
"""

    def _draft_pagare(self, cid, pa_name, pa_id, pb_name, pb_id, amount, curr, city, date_str) -> str:
        return f"""# {cid}
## PAGARÉ A LA ORDEN

- **No. de Pagaré**: `{cid}`
- **Valor Nominal**: `${amount:,.2f} {curr}`
- **Lugar de Pago**: {city}
- **Fecha de Emisión**: {date_str}

Yo, **{pb_name}**, identificado con NIT/C.C. No. **{pb_id}**, prometo pagar incondicionalmente a la orden de **{pa_name}**, identificado con C.C. No. **{pa_id}**, o a quien represente sus derechos, la suma cierta de **${amount:,.2f} {curr}**, por concepto de obligaciones comerciales contraídas.

El no pago puntual de la obligación generará intereses de mora a la tasa máxima legal permitida por la Superintendencia Financiera de Colombia.

Firma del Deudor: _________________________________________  
**{pb_name}** • Documento: {pb_id}
"""

    def _draft_acta(self, cid, pa_name, pb_name, scope, amount, curr, city, date_str) -> str:
        return f"""# {cid}
## ACTA DE ENTREGA Y LIQUIDACIÓN A SATISFACCIÓN

En {city}, a los {date_str}, se reúnen las partes intervinientes para formalizar la entrega a entera satisfacción de los entregables correspondientes a:
> **{scope}**.

1. **Cumplimiento**: El contratante certifica que los entregables han sido recibidos y cumplen con las especificaciones acordadas.
2. **Paz y Salvo**: Una vez efectuado el desembolso por valor de **${amount:,.2f} {curr}**, las partes declaran encontrarse a paz y salvo por todo concepto.

| Firma de Conformidad Contratante | Firma Consultor |
| :--- | :--- |
| {pb_name} | {pa_name} |
"""


# Global singleton instance
legal_contracts_service = LegalContractsService()
