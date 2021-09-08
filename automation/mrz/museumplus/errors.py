class MuseumPlusError(Exception):
    """
    General MuseumPlus error class to provide a superclass for all other errors
    """


class XMLParsingError(MuseumPlusError):
    """
    The error raised when parsing the XML.
    """