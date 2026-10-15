# Evidencia TDD — recursos

1. **RED:** `python -m unittest tests.test_assets -v` produjo 4 fallos de aserción: faltaba `assets/manifest.json`. No fue fallo de importación ni dependencia ausente.
2. Se descargaron recursos públicos a `/private/tmp/rpg2d-assets`, se inspeccionaron GIF/PNG con Pygame y `view_image`, y se incorporó únicamente la selección necesaria con manifiesto y licencias.
3. **Descubrimiento de contrato:** los cuatro OGG originales duran exactamente 6 s. La primera restricción arbitraria `<6` se reemplazó por verificación contra duración declarada real (`duration_seconds:6.0`); no se modificó audio para satisfacer una suposición incorrecta.
4. **GREEN:** `python -m unittest tests.test_assets -v`: 4 pruebas aprobadas. Pruebas con mixer dummy, sin build y sin afirmar validación auditiva.
5. El manifiesto separa imágenes reales, placeholders dibujados por código y packs SBS no integrados por HTTP 429.
