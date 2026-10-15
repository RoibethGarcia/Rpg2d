#!/bin/bash
# Captura OPT-IN. No se llama desde tests ni desde la aplicación.
set -eu
if [ "${1:-}" != "--record" ] || [ "$#" -ne 1 ]; then
    printf '%s\n' 'Uso: bash scripts/grabar_video.sh --record' \
      'Abre primero el juego. La captura interactiva dura 25 segundos.' \
      'Selecciona SOLO la ventana del juego; nunca el escritorio ni datos privados.' \
      'Sin --record no se inicia captura alguna.'
    exit 0
fi
if [ "$(uname -s)" != Darwin ] || [ ! -x /usr/sbin/screencapture ]; then
    printf '%s\n' 'Esta ayuda requiere la herramienta nativa screencapture de macOS.' >&2
    exit 1
fi
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUTPUT="$ROOT/artifacts/demo.mov"
if [ -e "$OUTPUT" ]; then
    printf '%s\n' "Ya existe $OUTPUT. Muévelo o elige otra entrega antes de grabar; no se sobrescribe." >&2
    exit 1
fi
mkdir -p "$ROOT/artifacts"
printf '%s\n' 'Mantén abierto el juego y oculta notificaciones/datos privados.' \
  'Selecciona SOLO la ventana del juego; Espacio cambia a selección de ventana.' \
  'Si no puedes aislarla, cancela con Escape. Puede solicitar permiso de pantalla.' \
  'No se activa micrófono ni se garantiza audio de sistema en este comando.'
/usr/sbin/screencapture -v -V25 -i "$OUTPUT"
if [ ! -s "$OUTPUT" ]; then
    printf '%s\n' 'No se obtuvo video: selección cancelada o permiso no concedido.' >&2
    exit 1
fi
printf '%s\n' "Archivo guardado: $OUTPUT" \
  'Revísalo antes de entregar: duración 15–40 s, solo juego, legibilidad y sonido.' \
  'artifacts/ está excluido de Git; grabar NO publica ni entrega el archivo.'
