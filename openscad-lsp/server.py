"""
This is a language server for OpenSCAD.
"""

import asyncio
import time

from pygls.features import (COMPLETION, TEXT_DOCUMENT_DID_CHANGE,
                            TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN)
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem, CompletionList, CompletionParams, ConfigurationItem,
    ConfigurationParams, Diagnostic, DidChangeTextDocumentParams,
    DidCloseTextDocumentParams, DidOpenTextDocumentParams, Position, Range)

COUNT_DOWN_START_IN_SECONDS = 10
COUNT_DOWN_SLEEP_IN_SECONDS = 1


class OpenscadLanguageServer(LanguageServer):
    CMD_COUNT_DOWN_BLOCKING = 'countDownBlocking'
    CMD_COUNT_DOWN_NON_BLOCKING = 'countDownNonBlocking'
    CMD_SHOW_CONFIGURATION_ASYNC = 'showConfigurationAsync'
    CMD_SHOW_CONFIGURATION_CALLBACK = 'showConfigurationCallback'
    CMD_SHOW_CONFIGURATION_THREAD = 'showConfigurationThread'

    CONFIGURATION_SECTION = 'openscadServer'

    def __init__(self):
        super().__init__()


openscad_server = OpenscadLanguageServer()


def _validate(ls, params):
    ls.show_message_log('Validating OpenSCAD...')

    text_doc = ls.workspace.get_document(params.textDocument.uri)

    source = text_doc.source
    diagnostics = _validate_openscad(source) if source else []

    ls.publish_diagnostics(text_doc.uri, diagnostics)


def _validate_openscad(source):
    """Validates OpenSCAD file."""
    #  diagnostics = []

    #  try:
    #      json.loads(source)
    #  except JSONDecodeError as err:
    #      msg = err.msg
    #      col = err.colno
    #      line = err.lineno
    #
    #      d = Diagnostic(
    #          Range(Position(line - 1, col - 1), Position(line - 1, col)),
    #          msg,
    #          source=type(json_server).__name__)
    #
    #      diagnostics.append(d)

    return None


@openscad_server.feature(COMPLETION)
def completions(params: CompletionParams = None):
    """Returns completion items."""
    return CompletionList(False, [
        CompletionItem('"'),
        CompletionItem('elephant'),
        CompletionItem('function'),
        CompletionItem('module'),
        CompletionItem('{'),
        CompletionItem('}')
    ])


@openscad_server.command(OpenscadLanguageServer.CMD_COUNT_DOWN_BLOCKING)
def count_down_10_seconds_blocking(ls, *args):
    """Starts counting down and showing message synchronously.
    It will `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message(
            'Counting down... {}'.format(COUNT_DOWN_START_IN_SECONDS - i))
        time.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


@openscad_server.command(OpenscadLanguageServer.CMD_COUNT_DOWN_NON_BLOCKING)
async def count_down_10_seconds_non_blocking(ls, *args):
    """Starts counting down and showing message asynchronously.
    It won't `block` the main thread, which can be tested by trying to show
    completion items.
    """
    for i in range(COUNT_DOWN_START_IN_SECONDS):
        ls.show_message(
            'Counting down... {}'.format(COUNT_DOWN_START_IN_SECONDS - i))
        await asyncio.sleep(COUNT_DOWN_SLEEP_IN_SECONDS)


@openscad_server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls, params: DidChangeTextDocumentParams):
    """Text document did change notification."""
    _validate(ls, params)


@openscad_server.feature(TEXT_DOCUMENT_DID_CLOSE)
def did_close(server: OpenscadLanguageServer,
              params: DidCloseTextDocumentParams):
    """Text document did close notification."""
    server.show_message('Text Document Did Close')


@openscad_server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    ls.show_message('Text Document Did Open')
    _validate(ls, params)


@openscad_server.command(OpenscadLanguageServer.CMD_SHOW_CONFIGURATION_ASYNC)
async def show_configuration_async(ls: OpenscadLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using coroutines."""
    try:
        config = await ls.get_configuration_async(
            ConfigurationParams([
                ConfigurationItem('',
                                  OpenscadLanguageServer.CONFIGURATION_SECTION)
            ]))

        example_config = config[0].exampleConfiguration

        ls.show_message('openscadServer.exampleConfiguration value: {}'.format(
            example_config))

    except Exception as e:
        ls.show_message_log('Error ocurred: {}'.format(e))


@openscad_server.command(
    OpenscadLanguageServer.CMD_SHOW_CONFIGURATION_CALLBACK)
def show_configuration_callback(ls: OpenscadLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using callback."""

    def _config_callback(config):
        try:
            example_config = config[0].exampleConfiguration

            ls.show_message(
                'openscadServer.exampleConfiguration value: {}'.format(
                    example_config))

        except Exception as e:
            ls.show_message_log('Error ocurred: {}'.format(e))

    ls.get_configuration(
        ConfigurationParams([
            ConfigurationItem('', OpenscadLanguageServer.CONFIGURATION_SECTION)
        ]), _config_callback)


@openscad_server.thread()
@openscad_server.command(OpenscadLanguageServer.CMD_SHOW_CONFIGURATION_THREAD)
def show_configuration_thread(ls: OpenscadLanguageServer, *args):
    """Gets exampleConfiguration from the client settings using thread pool."""
    try:
        config = ls.get_configuration(
            ConfigurationParams([
                ConfigurationItem('',
                                  OpenscadLanguageServer.CONFIGURATION_SECTION)
            ])).result(2)

        example_config = config[0].exampleConfiguration

        ls.show_message('openscadServer.exampleConfiguration value: {}'.format(
            example_config))

    except Exception as e:
        ls.show_message_log('Error ocurred: {}'.format(e))
