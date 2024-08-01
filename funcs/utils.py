from datetime import datetime
import zipfile


def zipper(file_list,zipname):
    with zipfile.ZipFile(zip_file,"w",
                    ) as zipMe:
                        for file in file_list:
                            zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)
    return zip_file


def get_periode(start_date,end_date):
    
    month_translation = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember"
}
    
    # start_date = datetime.strptime(start_date, "%Y-%m-%d")
    # end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # Extract year, month, and day
    start_day = start_date.day
    start_month = start_date.month
    start_year = start_date.year

    end_day = end_date.day
    end_month = end_date.month
    end_year = end_date.year

    # Get month names in Indonesian
    start_month_name = month_translation[start_month]
    end_month_name = month_translation[end_month]

    # Format the output based on whether dates are in the same month or different months
    if start_year == end_year and start_month == end_month:
        # Same month
        return f"{start_day}-{end_day} {start_month_name} {start_year}"
    else:
        # Different months
        return f"{start_day} {start_month_name} - {end_day} {end_month_name} {end_year}"
