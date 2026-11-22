extends Node
## Mod de la comunidad: agrega "Español" como idioma adicional de Crownhold.
## Se registra como autoload. No reemplaza ningún idioma del juego.

const LOCALE := "es"
const LABEL := "Español"
const META := "mod_es"
const CFG_PATH := "user://mod_espanol.cfg"
const OPTION_NAMES := ["LanguageOption", "LanguageOptionButton"]

var active := false
var _hooked: Array[int] = []
var _timer := 0.0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if not TranslationServer.get_loaded_locales().has(LOCALE):
		var res = load("res://translation.es.translation")
		if res:
			TranslationServer.add_translation(res)
	var cfg := ConfigFile.new()
	if cfg.load(CFG_PATH) == OK:
		active = bool(cfg.get_value("mod", "active", false))
	get_tree().node_added.connect(_on_node_added)
	if active:
		_apply_es.call_deferred()


func _process(delta: float) -> void:
	_timer += delta
	if _timer < 0.25:
		return
	_timer = 0.0
	if active and TranslationServer.get_locale() != LOCALE:
		_apply_es()
	for id in _hooked.duplicate():
		var o = instance_from_id(id)
		if o is OptionButton and is_instance_valid(o):
			_ensure_item(o)
		else:
			_hooked.erase(id)


func _set_active(value: bool) -> void:
	active = value
	var cfg := ConfigFile.new()
	cfg.set_value("mod", "active", value)
	cfg.save(CFG_PATH)


func _apply_es() -> void:
	if not active or TranslationServer.get_locale() == LOCALE:
		return
	TranslationServer.set_locale(LOCALE)
	_refresh()


func _refresh() -> void:
	get_tree().call_group("locale_aware", "apply_translations")


func _on_node_added(node: Node) -> void:
	if node is OptionButton and String(node.name) in OPTION_NAMES:
		_hook_later(node)


func _hook_later(opt: OptionButton) -> void:
	# Esperar a que el menú termine su _ready y conecte sus señales.
	await get_tree().process_frame
	await get_tree().process_frame
	if is_instance_valid(opt):
		_hook(opt)


func _hook(opt: OptionButton) -> void:
	if not opt.has_meta(META):
		opt.set_meta(META, true)
		var originals: Array = []
		for c in opt.item_selected.get_connections():
			var cb: Callable = c["callable"]
			if cb.get_object() == self:
				continue
			originals.append(cb)
			opt.item_selected.disconnect(cb)
		opt.item_selected.connect(_on_item_selected.bind(opt, originals))
	var id := opt.get_instance_id()
	if not _hooked.has(id):
		_hooked.append(id)
	_ensure_item(opt)


func _find_item(opt: OptionButton) -> int:
	for i in opt.item_count:
		if opt.get_item_metadata(i) is String and opt.get_item_metadata(i) == META:
			return i
		if opt.get_item_text(i) == LABEL:
			return i
	return -1


func _ensure_item(opt: OptionButton) -> void:
	var idx := _find_item(opt)
	if idx == -1:
		opt.add_item(LABEL)
		idx = opt.item_count - 1
		opt.set_item_metadata(idx, META)
	if active and opt.selected != idx:
		opt.select(idx)


func _on_item_selected(index: int, opt: OptionButton, originals: Array) -> void:
	if index == _find_item(opt):
		_set_active(true)
		_apply_es()
		return
	_set_active(false)
	for cb in originals:
		if cb.is_valid():
			cb.call(index)
	# Si el juego no cambió el idioma (porque ya era el suyo), lo restauramos nosotros.
	if TranslationServer.get_locale() == LOCALE:
		var loc := "en"
		var ps = get_node_or_null("/root/PlayerSettings")
		if ps and ps.has_method("get_locale"):
			loc = str(ps.get_locale())
		TranslationServer.set_locale(loc)
		_refresh()
