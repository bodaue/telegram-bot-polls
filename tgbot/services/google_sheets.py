from gspread_asyncio import AsyncioGspreadClient, AsyncioGspreadSpreadsheet, AsyncioGspreadWorksheet


async def create_spreadsheet(client: AsyncioGspreadClient, spreadsheet_name: str):
    spreadsheet = await client.create(spreadsheet_name)
    spreadsheet = await client.open_by_key(spreadsheet.id)

    return spreadsheet


async def add_worksheet(async_spreadsheet: AsyncioGspreadSpreadsheet,
                        worksheet_name: str):
    worksheet = await async_spreadsheet.add_worksheet(worksheet_name, rows=1000, cols=100)
    return worksheet


async def share_spreadsheet(async_spreadsheet: AsyncioGspreadSpreadsheet,
                            email: str, role: str = 'writer', perm_type: str = 'user'):
    await async_spreadsheet.share(email, perm_type=perm_type, role=role)


async def write_to_sheet(worksheet: AsyncioGspreadWorksheet, *args):
    await worksheet.append_row([*args])
