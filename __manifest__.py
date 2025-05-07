{
    "name":"Recursos Humanos",
    "description": "Modulo dedicado para recursos humanos",
    # "depends":["dtm_odt",'base', 'mail'],
    "data":[
        'security/ir.model.access.csv',
        'views/dtm_empleados_view.xml',
        'views/dtm_ano_laboral_view.xml',
        'views/dtm_bajas_view.xml',
        'views/dtm_menu_views.xml',
        'views/dtm_hr_indicadores_view.xml',
        'views/dtm_ht_rotacion_view.xml',
        'views/indicadores_view.xml',
        'views/rotacion_view.xml',

    ],'assets': {
        'web.assets_backend': [
            'dtm_hr/static/src/scc/styles.css',
            'dtm_hr/static/src/xml/indicador.xml',
            'dtm_hr/static/src/xml/rotacion.xml',
            'dtm_hr/static/src/js/indicador.js',
            'dtm_hr/static/src/js/rotacion.js',
        ],
    },
    'license': 'LGPL-3',
}
