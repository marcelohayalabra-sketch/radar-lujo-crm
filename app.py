if lanzar:
    with st.spinner("Escaneando Idealista... un momento, Señor Marcelo ⏳"):
        try:
            propiedades = idealista_apify.obtener_datos()
            scan_id, resumen = radar_db.run_scan(propiedades)
            st.success(f"✅ Escaneo completado · {resumen['created']} nuevas · {resumen['updated']} actualizadas · {resumen['total']} total")
            cambios = radar_db.get_changes_for_scan(scan_id)

            if cambios["nuevos"]:
                st.markdown('<div class="section-title" style="margin-top:24px">Propiedades nuevas detectadas</div>', unsafe_allow_html=True)
                for p in cambios["nuevos"]:
                    intermediario = safe_str(p.get("intermediario"), "N/A")
                    es_part = "particular" in intermediario.lower()
                    badge = '<span class="badge-particular">Particular</span>' if es_part else '<span class="badge-agencia">Agencia</span>'
                    clase = "verde" if es_part else "amarillo"
                    st.markdown(f"""
                    <div class="prop-card {clase}">
                      <div style="flex:1">
                        <div class="prop-dir">{safe_str(p.get("zona"))} {badge}</div>
                        <div class="prop-meta">{safe_str(p.get("direccion","N/A"))} · {safe_int(p.get("m2"))} m² · {safe_int(p.get("habitaciones"))} hab</div>
                      </div>
                      <div style="text-align:right">
                        <div class="prop-precio">{int(float(p.get("last_price",0))):,} €</div>
                        <a href="{safe_str(p.get("enlace"))}" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver →</a>
                      </div>
                    </div>""", unsafe_allow_html=True)

            if cambios["bajadas"]:
                st.markdown('<div class="section-title" style="margin-top:24px">Bajadas de precio</div>', unsafe_allow_html=True)
                for b in cambios["bajadas"]:
                    st.markdown(f"""
                    <div class="prop-card amarillo">
                      <div style="flex:1">
                        <div class="prop-dir">{safe_str(b.get("zona"))} <span class="badge-agencia">Bajada {b['bajada_pct']:.1f}%</span></div>
                        <div class="prop-meta">{safe_str(b.get("direccion","N/A"))}</div>
                      </div>
                      <div style="text-align:right">
                        <div class="prop-precio" style="text-decoration:line-through;color:#bbb;font-size:14px">{int(b['precio_anterior']):,} €</div>
                        <div class="prop-precio">{int(b['precio_actual']):,} €</div>
                        <a href="{safe_str(b.get("enlace"))}" target="_blank" style="font-size:11px;color:#C9A84C;letter-spacing:1px;">Ver →</a>
                      </div>
                    </div>""", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error durante el escaneo: {e}")
