-- fixlinks.lua
-- for production builds, prepend link and img src targets with the site's base url
-- see: https://stackoverflow.com/questions/48569597/

function fix_path (path)
  -- ignore paths that are already prefixed
  if path:sub(1, #"http") == "http" then
    return path
  end
  return (os.getenv('LINK_PREFIX') or '') .. path
end

function Link (element)
  element.target = fix_path(element.target)
  return element
end

function Image (element)
  element.src = fix_path(element.src)
  return element
end
