obs = obslua
source_name = ""
filename = "PATH TO SPOTIFY OUTPUT"

-- Function to see if the file exists
function file_exists(file)
    local f = io.open(file, "rb")
    if f then f:close() end
    return f ~= nil
end

-- Function to set the track id
function set_track_id()
    -- Make sure the file exists
    if not file_exists(filename) then return {} end
    local f = io.open(filename, "rb")
    local content = f:read("*all")
    f:close()

    local source = obs.obs_get_source_by_name(source_name)
    if source ~= nil then
        local settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", content)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)
    end
end

function activate(activating)
    if activating then
        obs.timer_add(set_track_id, 1000)
    else
        obs.timer_remove(timer_callback)
    end
end

-- Called when a source is activated/deactivated
function activate_signal(cd, activating)
    local source = obs.calldata_source(cd, "source")
    if source ~= nil then
        local name = obs.obs_source_get_name(source)
        if (name == source_name) then
            activate(activating)
        end
    end
end

function source_activated(cd)
    activate_signal(cd, true)
end

function source_deactivated(cd)
    activate_signal(cd, false)
end


-- A function named script_properties defines the properties that the user
-- can change for the entire script module itself
function script_properties()
    local props = obs.obs_properties_create()
    local p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    local sources = obs.obs_enum_sources()
    if sources ~= nil then
        for _, source in ipairs(sources) do
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source" then
                local name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)
            end
        end
    end
    obs.source_list_release(sources)

    return props
end

-- A function named script_description returns the description shown to the user
function script_description()
    return "Sets a text source to act as a Spotify Track ID when the source is active."
end

-- A function named script_update will be called when settings are changed
function script_update(settings)
    source_name = obs.obs_data_get_string(settings, "source")
end

-- A function named script_load will be called on startup
function script_load(settings)
    -- Connect activation/deactivation signal callbacks
    local sh = obs.obs_get_signal_handler()
    obs.signal_handler_connect(sh, "source_activate", source_activated)
    obs.signal_handler_connect(sh, "source_deactivate", source_deactivated)

    -- Check if the source is active, if so then activate it
    if source_name ~= "" then
        local source = obs.obs_get_source_by_name(source_name)
        if source ~= nil and obs.obs_source_active(source) then
            activate(true)
        else
            activate(false)
        end
    else
        activate(false)
    end
end
