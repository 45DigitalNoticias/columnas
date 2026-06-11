// ============================================================
// Inseguridad México · constantes compartidas del sitio
// Decisiones de diseño fijadas (sesión 9-jun-2026):
//  - Tile map como mapa principal (no coroplético geográfico)
//  - Escala ÁMBAR DE MARCA: un matiz, 5 luminosidades, bins por
//    cuantiles. El bin superior lleva glow.
//  - Identidad por estado: solo como acento (hero de página-estado
//    y siluetas), nunca como codificación del mapa.
// ============================================================

// ============================================================
// MAPA NACIONAL · DECISIÓN FINAL (9-jun-2026, 6 iteraciones):
// CAMPO INTERPOLADO estilo meteorológico (IDW) + espectro completo.
// - El valor de cada estado se interpola como campo de temperatura
//   (IDW potencia 2.8 sobre rank-t de centroides) → el color FLUYE
//   entre estados como en mapas del clima.
// - Espectro: azul profundo (tenue) → verde → amarillo → rojo vino (intenso)
// - Bordes estatales blancos finos encima + valor numérico por estado
// - Render: canvas raster (1/4 resolución + upscale suave) + máscara
//   del país con UN SOLO Path2D combinado (destination-in)
// - Nota editorial obligatoria al pie: la interpolación es estética;
//   el dato real es el número impreso por estado.
// ============================================================
const ESCALA_METEO = ['#1a2db0','#2e6fde','#35b5e8','#3dbb6e','#8bc63f','#f3e13a','#fbb03b','#f4711f','#e02f1f','#a31212','#6e0b0b'];
const IDW_POW = 2.8;     // potencia de la interpolación
const IDW_DOWNSCALE = 4; // cómputo a 1/4 de resolución + upscale

// Abreviaturas oficiales por clave INEGI
const ABREV_ENT = {1:'AGS',2:'BC',3:'BCS',4:'CAMP',5:'COAH',6:'COL',7:'CHIS',8:'CHIH',9:'CDMX',10:'DGO',11:'GTO',12:'GRO',13:'HGO',14:'JAL',15:'MEX',16:'MICH',17:'MOR',18:'NAY',19:'NL',20:'OAX',21:'PUE',22:'QRO',23:'QROO',24:'SLP',25:'SIN',26:'SON',27:'TAB',28:'TAM',29:'TLAX',30:'VER',31:'YUC',32:'ZAC'};

// Tile map · layout geográfico aproximado · grid 8 col × 5 filas
// clave INEGI → [col, fila]
const TILEPOS_ENT = {
  2:[0,0], 26:[1,0], 8:[2,0], 5:[3,0], 19:[4,0], 28:[5,0],
  3:[0,1], 25:[1,1], 10:[2,1], 32:[3,1], 24:[4,1], 30:[5,1], 31:[7,1],
  18:[1,2], 14:[2,2], 1:[3,2], 11:[4,2], 22:[5,2], 13:[6,2], 23:[7,2],
  6:[1,3], 16:[2,3], 15:[3,3], 9:[4,3], 29:[5,3], 21:[6,3], 4:[7,3],
  12:[2,4], 17:[3,4], 20:[4,4], 27:[5,4], 7:[6,4],
};

// Cortes por cuantiles (4 cortes → 5 bins)
function binsCuantiles(valores){
  const s = valores.slice().sort((a,b)=>a-b);
  const q = k => s[Math.min(s.length-1, Math.floor(k*s.length))];
  return [q(0.2), q(0.4), q(0.6), q(0.8)];
}
function binDeValor(v, cortes){
  let i = 0; while (i < cortes.length && v > cortes[i]) i++;
  return i;
}

// Nombre corto editorial (sin sufijos largos)
function nombreCorto(entidad){
  return String(entidad).replace(' de Zaragoza','').replace(' de Ocampo','').replace(' de Ignacio de la Llave','');
}
