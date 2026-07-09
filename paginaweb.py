import streamlit as st
import urllib.parse  # Para crear el mensaje de WhatsApp de forma segura

# =====================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero)
# =====================================================================
st.set_page_config(
    page_title="closet miri products", 
    layout="wide",
    initial_sidebar_state="collapsed" # Oculta la barra lateral predeterminada
)

# --- INICIALIZAR ESTADOS DE SESIÓN INDIVIDUALES ---
if "producto_seleccionado" not in st.session_state:
    st.session_state.producto_seleccionado = None

if "foto_principal_detalle" not in st.session_state:
    st.session_state.foto_principal_detalle = None

if "carrito" not in st.session_state:
    st.session_state.carrito = []  # Bolsa de compras temporal por pestaña

if "viendo_carrito" not in st.session_state:
    st.session_state.viendo_carrito = False

# --- CONFIGURACIÓN DE TU WHATSAPP ---
# REEMPLAZA ESTE NÚMERO POR EL TUYO: Código de país (52 para México) + tus 10 dígitos. Sin espacios ni signos +
TELEFONO_WHATSAPP = "527298272377" 

# =====================================================================
# 2. CATÁLOGO DE PRODUCTOS (¡Edita aquí tus productos de forma segura!)
# =====================================================================
CATALOGO = {
    "Maquillaje": [
        {
            "id": "maq_1",
            "tag": "Lo más vendido",
            "title": "Labial Líquido Mate Indeleble Forever",
            "subtitle": "Labial líquido de larga duración con Vitamina B5",
            "price": "$452.00 MXN",
            "precio_anterior": "$600.00 MXN",
            "calificacion": "⭐⭐⭐⭐⭐",
            "descripcion": "Labial líquido Mate Indeleble con Vitamina B5 7 g e. 24 oz. (1.86 x 1.86 x 10.50 cm)",
            "imagen": "https://lbelmexico.vtexassets.com/arquivos/ids/1164889-500-auto?v=639175334237900000&width=500&height=auto&aspect=true", # Reemplazar por tu imagen ej: "base.jpg"
            "galeria": [
                "https://belcorpmexico.vtexassets.com/arquivos/ids/1164885-1600-auto?v=639175334233400000&width=1600&height=auto&aspect=true",
                "https://belcorpmexico.vtexassets.com/arquivos/ids/1164886-1600-auto?v=639175334234800000&width=1600&height=auto&aspect=true",
                "https://belcorpmexico.vtexassets.com/arquivos/ids/1164887-1600-auto?v=639175334235900000&width=1600&height=auto&aspect=true"
            ]
        }
    ],
    "Ropa y Tenis": [
        {
            "id": "tenis_1",
            "tag": "Materiales reciclados",
            "title": "Nike Air Max Muse",
            "subtitle": "Tenis para mujer",
            "price": "$3,299.00 MXN",
            "precio_anterior": "$3,800.00 MXN",
            "calificacion": "⭐⭐⭐⭐⭐ (89)",
            "descripcion": "Diseño futurista inspirado en la era Y2K. Cuenta con la clásica amortiguación Air Max que brinda comodidad absoluta.",
            "imagen": "https://placehold.co/600x600/f6f6f6/888888?text=Air+Max+1", # Reemplazar por tu imagen ej: "tenis1.jpg"
            "galeria": [
                "https://placehold.co/600x600/f6f6f6/888888?text=Air+Max+1"
            ]
        }
    ],
    "Perfumes": [
        {
            "id": "perf_1",
            "tag": "Top Sellers",
            "title": "Bleu Night Perfume para Hombre 100 ml.",
            "subtitle": "Perfume de alta concentración",
            "price": "$663.00 MXN",
            "precio_anterior": "$780.00 MXN",
            "calificacion": "⭐⭐⭐⭐⭐",
            "descripcion": "Perfume fresco para hombre de muy alta concentración de la familia olfativa herbal maderoso. Notas intensas que perduran todo el día.",
            "imagen": "https://belcorpmexico.vtexassets.com/arquivos/ids/1157847-500-auto?v=639175215758830000&width=500&height=auto&aspect=true", # Reemplazar por tu imagen ej: "bleunight.jpg"
            "galeria": [
                "https://belcorpmexico.vtexassets.com/arquivos/ids/1157844-1600-auto?v=639175215755400000&width=1600&height=auto&aspect=true",
                "https://belcorpmexico.vtexassets.com/arquivos/ids/1157845-1600-auto?v=639175215756930000&width=1600&height=auto&aspect=true",
                "https://belcorpmexico.vtexassets.com/arquivos/ids/1157846-1600-auto?v=639175215757900000&width=1600&height=auto&aspect=true"
            ]
        }
    ]
}

# =====================================================================
# 3. SISTEMA DE USUARIO PRIVADO (Query Params en la URL)
# =====================================================================
# Leemos el nombre directamente de la URL del navegador del cliente
nombre_actual = st.query_params.get("nombre", "")

def guardar_nombre_en_url(nombre):
    st.query_params["nombre"] = nombre

def borrar_nombre_de_url():
    st.query_params.clear()

# --- FUNCIONES DE LA BOLSA DE COMPRAS ---
def limpiar_precio_a_numero(precio_str):
    try:
        limpio = precio_str.replace("$", "").replace("MXN", "").replace(",", "").strip()
        return float(limpio)
    except:
        return 0.0

def agregar_al_carrito(producto, cantidad):
    precio_num = limpiar_precio_a_numero(producto.get("price", "0"))
    for item in st.session_state.carrito:
        if item["id"] == producto["id"]:
            item["cantidad"] += cantidad
            item["total_item"] = item["cantidad"] * precio_num
            return
            
    st.session_state.carrito.append({
        "id": producto["id"],
        "title": producto.get("title", "Producto"),
        "precio_texto": producto.get("price", "$0.00"),
        "precio_unitario": precio_num,
        "cantidad": cantidad,
        "total_item": cantidad * precio_num,
        "imagen": producto.get("imagen", "")
    })

# =====================================================================
# 4. ESTILOS VISUALES (CSS Personalizado)
# =====================================================================
st.markdown("""
<style>
    /* Ocultar barra lateral nativa */
    [data-testid="collapsedControl"] { display: none; }
    .stApp { background-color: #121212; color: #ffffff; }
    
    /* Contenedor de Cristal (Pantalla de Bienvenida) */
    .contenedor-cristal {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 60px 40px;
        text-align: center;
        margin-top: 80px;
        max-width: 800px;
        margin-left: auto; margin-right: auto;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* Estilos Catálogo */
    .etiqueta-tag { color: #ff5a36; font-size: 0.95rem; font-weight: 700; margin-bottom: 2px; }
    .titulo-prod { color: #ffffff; font-size: 1.15rem; font-weight: 600; margin-bottom: 1px; }
    .subtitulo-prod { color: #757575; font-size: 1rem; margin-bottom: 4px; }
    .precio-prod { color: #ffffff; font-size: 1.15rem; font-weight: 500; margin-bottom: 10px; }
    
    /* Estilos Detalle */
    .badge-detalle { background-color: #7c3aed; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; display: inline-block; margin-bottom: 15px; }
    .titulo-detalle { font-size: 2.2rem; font-weight: 700; line-height: 1.2; margin-bottom: 5px; }
    .calif-detalle { color: #ffb400; font-size: 1rem; margin-bottom: 20px; }
    .seccion-descripcion { border-top: 1px solid #333; border-bottom: 1px solid #333; padding: 20px 0; margin-bottom: 20px; }
    .precio-anterior { text-decoration: line-through; color: #757575; font-size: 1.2rem; margin-right: 10px; }
    .precio-actual { color: #ffffff; font-size: 1.8rem; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# 5. CONTROL DE PÁGINAS (FLUJO)
# =====================================================================

# --- PÁGINA 1: INICIO (CRISTAL - Si no hay nombre en la URL) ---
if not nombre_actual:
    st.markdown('<div class="contenedor-cristal">', unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 3.5rem; font-weight: 800;'>closet miri products</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.3rem; color: #b3b3b3;'>Te damos la bienvenida. Ingresa tu nombre para comenzar:</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        nombre_input = st.text_input("Nombre", label_visibility="collapsed", placeholder="Tu nombre aquí...")
        if st.button("Entrar a la tienda", use_container_width=True):
            if nombre_input.strip():
                # Guardamos el nombre en la URL del cliente actual
                guardar_nombre_en_url(nombre_input.strip())
                st.rerun() # Reinicia mostrando la tienda personalizada
            else:
                st.error("Por favor, escribe un nombre válido.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PÁGINA 2: LA BOLSA DE COMPRAS ---
elif st.session_state.viendo_carrito:
    if st.button("← Volver a la Tienda"):
        st.session_state.viendo_carrito = False
        st.rerun()
        
    st.title("🛍️ Tu Bolsa de Compras")
    st.write("---")
    
    if len(st.session_state.carrito) == 0:
        st.subheader("Tu bolsa está vacía. ¡Explora el catálogo para añadir productos!")
    else:
        subtotal = 0.0
        
        for idx, item in enumerate(st.session_state.carrito):
            col_img, col_detalles, col_eliminar = st.columns([1, 3, 1])
            with col_img:
                st.image(item["imagen"], width=100)
            with col_detalles:
                st.markdown(f"### {item['title']}")
                st.write(f"Precio Unitario: **{item['precio_texto']}**")
                st.write(f"Cantidad: **{item['cantidad']}**")
                st.write(f"Total: **${item['total_item']:,.2f} MXN**")
                subtotal += item["total_item"]
            with col_eliminar:
                st.write("") # Espaciador
                if st.button("🗑️ Eliminar", key=f"del_{idx}"):
                    st.session_state.carrito.pop(idx)
                    st.rerun()
            st.write("---")
            
        st.markdown(f"## Total a Pagar: <span style='color:#00e676;'>${subtotal:,.2f} MXN</span>", unsafe_allow_html=True)
        st.write("")
        
        # --- MENSAJE DE WHATSAPP MEJORADO (CON NOMBRE DESTACADO) ---
        mensaje_pedido = (
            f"🌸 *NUEVO PEDIDO - CLOSET MIRI PRODUCTS* 🌸\n\n"
            f"👤 *Cliente:* {nombre_actual}\n"
            f"-----------------------------------------\n"
            f"📦 *Detalle de la compra:*\n"
        )
        for item in st.session_state.carrito:
            mensaje_pedido += f"• *{item['cantidad']}x* {item['title']} ({item['precio_texto']})\n"
            
        mensaje_pedido += (
            f"-----------------------------------------\n"
            f"💵 *Total estimado:* ${subtotal:,.2f} MXN\n\n"
            f"¡Muchas gracias! ✨"
        )
        
        mensaje_codificado = urllib.parse.quote(mensaje_pedido)
        enlace_final_wa = f"https://wa.me/{TELEFONO_WHATSAPP}?text={mensaje_codificado}"
        
        st.markdown(f"""
        <a href="{enlace_final_wa}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25d366; color:white; padding:15px; border-radius:10px; text-align:center; font-weight:bold; font-size:1.2rem; cursor:pointer;">
                🟢 Finalizar pedido y enviar por WhatsApp
            </div>
        </a>
        """, unsafe_allow_html=True)

# --- PÁGINA 3: DETALLE DE UN PRODUCTO (Estilo L'Bel con protección contra errores) ---
elif st.session_state.producto_seleccionado is not None:
    prod = st.session_state.producto_seleccionado
    
    if st.button("← Volver al catálogo"):
        st.session_state.producto_seleccionado = None
        st.session_state.foto_principal_detalle = None
        st.rerun()
        
    st.write("")
    
    col_miniaturas, col_foto_grande, col_info = st.columns([0.5, 2, 2.5])
    
    if st.session_state.foto_principal_detalle is None:
        st.session_state.foto_principal_detalle = prod.get("imagen", "")
        
    with col_miniaturas:
        st.write("<p style='font-size:0.8rem; color:#757575; text-align:center;'>Vistas</p>", unsafe_allow_html=True)
        imagenes_galeria = prod.get("galeria", [prod.get("imagen", "")])
        for idx, foto_url in enumerate(imagenes_galeria):
            if st.button("📷", key=f"mini_{idx}"):
                st.session_state.foto_principal_detalle = foto_url
                st.rerun()
                
    with col_foto_grande:
        st.image(st.session_state.foto_principal_detalle, use_container_width=True)
        
    with col_info:
        # Sistema de seguridad `.get()` para prevenir KeyErrors si te falta algún dato al editar
        tag_seguro = prod.get("tag", "Producto estrella")
        title_seguro = prod.get("title", "Producto sin nombre")
        calif_segura = prod.get("calificacion", "⭐⭐⭐⭐⭐ (5)")
        desc_segura = prod.get("descripcion", "No hay descripción disponible para este producto.")
        precio_ant_seguro = prod.get("precio_anterior", "")
        precio_seguro = prod.get("price", "$0.00")

        st.markdown(f'<div class="badge-detalle">{tag_seguro}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="titulo-detalle">{title_seguro}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="calif-detalle">{calif_segura}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="seccion-descripcion">
            <b style="font-size:1.1rem; color:#ffffff;">¿Qué es?</b><br>
            <p style="color:#b3b3b3; margin-top:5px; font-size:1rem; line-height:1.5;">{desc_segura}</p>
        </div>
        """, unsafe_allow_html=True)
        
        precios_html = ""
        if precio_ant_seguro:
            precios_html += f'<span class="precio-anterior">{precio_ant_seguro}</span>'
        precios_html += f'<span class="precio-actual">{precio_seguro}</span>'
        
        st.markdown(f"""
        <div style="margin-bottom: 25px;">
            {precios_html}
        </div>
        """, unsafe_allow_html=True)
        
        col_cant, col_btn_add = st.columns([1, 3])
        with col_cant:
            cantidad_selec = st.number_input("Cantidad", min_value=1, max_value=10, value=1, key=f"cant_{prod.get('id')}")
        with col_btn_add:
            st.write("") 
            if st.button("Agregar a la bolsa", key=f"btn_bolsa_{prod.get('id')}", type="primary"):
                agregar_al_carrito(prod, cantidad_selec)
                st.success("¡Agregado exitosamente a tu bolsa! 🛍️")

# --- PÁGINA 4: TIENDA GENERAL (Catálogo estilo Nike) ---
else:
    col_titulo, col_acciones = st.columns([0.6, 0.4])
    with col_titulo:
        st.markdown("<h1 style='margin-bottom: 0;'>closet miri products</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #b3b3b3;'>¡Hola, de nuevo, <b>{nombre_actual}</b>! ✨</p>", unsafe_allow_html=True)
    
    with col_acciones:
        st.write("") 
        articulos_en_bolsa = sum(item["cantidad"] for item in st.session_state.carrito)
        
        col_cart, col_logout = st.columns(2)
        with col_cart:
            texto_bolsa = f"🛍️ Mi Bolsa ({articulos_en_bolsa})"
            if st.button(texto_bolsa, use_container_width=True):
                st.session_state.viendo_carrito = True
                st.rerun()
        with col_logout:
            if st.button("Cerrar sesión", use_container_width=True):
                borrar_nombre_de_url() # Limpia la URL
                st.rerun()
            
    st.write("---")

    tab1, tab2, tab3 = st.tabs(["Maquillaje", "Ropa y Tenis", "Perfumes"])

    def renderizar_grid_nike(nombre_categoria):
        lista_productos = CATALOGO.get(nombre_categoria, [])
        if not lista_productos:
            st.info("Próximamente más productos.")
            return

        columnas = st.columns(3)
        for indice, producto in enumerate(lista_productos):
            with columnas[indice % 3]:
                st.image(producto.get('imagen', ''), use_container_width=True)
                
                st.markdown(f"""
                <div style="margin-top: -10px; padding-bottom: 5px;">
                    <div class="etiqueta-tag">{producto.get('tag', '')}</div>
                    <div class="titulo-prod">{producto.get('title', '')}</div>
                    <div class="subtitulo-prod">{producto.get('subtitle', '')}</div>
                    <div class="precio-prod">{producto.get('price', '')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Ver detalles del producto 🔎", key=f"btn_{producto.get('id')}", use_container_width=True):
                    st.session_state.producto_seleccionado = producto
                    st.rerun()

    with tab1: renderizar_grid_nike("Maquillaje")
    with tab2: renderizar_grid_nike("Ropa y Tenis")
    with tab3: renderizar_grid_nike("Perfumes")
