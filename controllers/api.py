from odoo import http # type: ignore
from odoo.http import request # type: ignore

class ApiController(http.Controller):
    @http.route('/api/login', type='json', auth='public', methods=['POST'], csrf=False)
    def authenticate(self):
        """
        Autentica a un jugador con nickname y password
        """
        try:
            import json
            request_data = json.loads(request.httprequest.data)
            nickname = request_data.get('nickname')
            password = request_data.get('password')

            if not nickname or not password:
                return self._response('Nickname y password son requeridos', 400)

            jugador = request.env['jugador'].sudo().search([('nickname', '=', nickname), ('password', '=', password)], limit=1)
            if not jugador:
                return self._response('Credenciales inválidas', 401)

            return self._response('Login exitoso', 200, {
                'id': jugador.id,
                'nickname': jugador.nickname,
                'coins': jugador.coins,
                'xp': jugador.xp,
                'level': jugador.level,
                'skins': jugador.skin_ids.read(['id', 'name'])
            })

        except Exception as e:
            return self._response('Error interno del servidor', 500, {'error': str(e)})

    def _response(self, message, code, data=None):
        """
        Genera una respuesta estándar para las rutas del controlador.
        """
        return {
            'status': 'success' if code == 200 else 'error',
            'message': message,
            'code': code,
            'data': data or {}
        }


    @http.route('/api/register', type='json', auth='public', methods=['POST'], csrf=False)
    def register_player(self):
        """
        Registra un nuevo jugador con nombre, correo, nickname y password


        """
        try:

            import json
            request_data = json.loads(request.httprequest.data)
            name = request_data.get('name')
            email = request_data.get('email')
            nickname = request_data.get('nickname')
            password = request_data.get('password')


            if not name or not email or not nickname or not password:
                return self._response('Nombre, email, nickname y password son requeridos', 400)

            existing_player = request.env['jugador'].sudo().search([('nickname', '=', nickname)], limit=1)
            if existing_player:
                return self._response(f'El nickname "{nickname}" ya está en uso.', 400)

            existing_email = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
            if existing_email:
                return self._response(f'El correo "{email}" ya está en uso.', 400)

            partner = request.env['res.partner'].sudo().create({
                'name': name,
                'email': email
            })

            jugador = request.env['jugador'].sudo().create({
                'nickname': nickname,
                'password': password,
                'coins': 150,
                'xp': 0,
                'level': 1,
                'partner_id': partner.id
            })

            return self._response('Registro exitoso', 200, {
                'id': jugador.id,
                'nickname': jugador.nickname,
                'coins': jugador.coins,
                'xp': jugador.xp,
                'level': jugador.level,
                'partner': {
                    'id': partner.id,
                    'name': partner.name,
                    'email': partner.email
                }
            })

        except Exception as e:
            return self._response('Error interno del servidor', 500, {'error': str(e)})


    def _response(self, message, code, data=None):
        """
        Genera una respuesta estándar para las rutas del controlador.
        """
        return {
            'status': 'success' if code == 200 else 'error',
            'message': message,
            'code': code,
            'data': data or {}
        }

    @http.route('/api/jugador', type='json', auth='public', methods=['GET'], csrf=False)
    def get_all_jugadores(self):
        """
        Obtiene todos los jugadores
        """
        jugadores = request.env['jugador'].sudo().search([])
        jugadores_data = jugadores.read(['id', 'nickname', 'coins', 'xp', 'level', 'skin_ids'])

        for jugador in jugadores_data:
            jugador['skins'] = request.env['skin'].sudo().browse(jugador['skin_ids']).read(['id', 'name'])
            jugador.pop('skin_ids', None)

        return self._response('Lista de jugadores obtenida exitosamente', 200, jugadores_data)

    def _response(self, message, code, data=None):
        """
        Genera una respuesta estándar para las rutas del controlador.
        """
        return {
            'status': 'success' if code == 200 else 'error',
            'message': message,
            'code': code,
            'data': data or {}
        }
    
    @http.route('/api/skin', type='json', auth='public', methods=['GET'], csrf=False)
    def get_all_skins(self):
        skins = request.env['skin'].sudo().search([])
        skins_data = []
        for skin in skins:
            skins_data.append({
                'id': skin.id,
                'name': skin.name,
                'price': skin.price,
                'image_url': f"https://odooxeo.duckdns.org/web/image/skin/{skin.id}/image.png"
            })

        
        return self._response('Lista de skins obtenida exitosamente', 200, skins_data)
    def _response(self, message, code, data=None):
        """
        Genera una respuesta estándar para las rutas del controlador.
        """
        return {
            'status': 'success' if code == 200 else 'error',
            'message': message,
            'code': code,
            'data': data or {}
        }
    
    @http.route('/api/jugador/add_skin', type='json', auth='public', methods=['PUT'], csrf=False)
    def add_skin_to_player(self):
        """
        Agrega una skin a un jugador
        """
        try:
            import json
            request_data = json.loads(request.httprequest.data)
            nickname = request_data.get('nickname')
            skin_name = request_data.get('skin_name')

            if not nickname or not skin_name:
                return self._response('Faltan parámetros nickname o skin_name.', 400)

            jugador = request.env['jugador'].sudo().search([('nickname', '=', nickname)], limit=1)
            skin = request.env['skin'].sudo().search([('name', '=', skin_name)], limit=1)

            if not jugador:
                return self._response(f'El jugador con nickname "{nickname}" no existe.', 404)

            if not skin:
                return self._response(f'La skin con nombre "{skin_name}" no existe.', 404)

            if skin in jugador.skin_ids:
                return self._response(f'El jugador "{nickname}" ya tiene la skin "{skin_name}".', 400)

            if jugador.coins < skin.price:
                return self._response(f'El jugador "{nickname}" no tiene suficientes coins para comprar la skin "{skin_name}".', 400)

            jugador.sudo().write({
                'skin_ids': [(4, skin.id)],
                'coins': jugador.coins - skin.price
            })

            jugador_data = {
                'jugador_id': jugador.id,
                'nickname': jugador.nickname,
                'coins': jugador.coins,
                'skins': [skin.name for skin in jugador.skin_ids]
            }

            return self._response(f'Skin "{skin.name}" añadida al jugador "{jugador.nickname}".', 200, jugador_data)

        except Exception as e:
            return self._response('Error interno del servidor', 500, {'error': str(e)})


    def _response(self, message, code, data=None):
        """
        Genera una respuesta estándar para las rutas del controlador.
        """
        return {
            'status': 'success' if code == 200 else 'error',
            'message': message,
            'code': code,
            'data': data or {}
        }

    @http.route('/api/jugador/update_password', type='json', auth='public', methods=['PUT'], csrf=False)
    def update_player_password(self):
        """
        Actualiza la contraseña de un jugador dado su nickname y nueva contraseña.
        """
        try:
            import json
            request_data = json.loads(request.httprequest.data)
            nickname = request_data.get('nickname')
            new_password = request_data.get('new_password')

            if not nickname or not new_password:
                return self._response('Faltan parámetros nickname o new_password.', 400)

            jugador = request.env['jugador'].sudo().search([('nickname', '=', nickname)], limit=1)

            if not jugador:
                return self._response(f'El jugador con nickname "{nickname}" no existe.', 404)

            jugador.sudo().write({'password': new_password})

            return self._response(f'Contraseña actualizada correctamente para el jugador "{nickname}".', 200)

        except Exception as e:
            return self._response('Error interno del servidor', 500, {'error': str(e)})

    def _response(self, message, code, data=None):
        """
        Genera una respuesta estándar para las rutas del controlador.
        """
        return {
            'status': 'success' if code == 200 else 'error',
            'message': message,
            'code': code,
            'data': data or {}
        }
