import random
import google_places_scrapper


def main():
    points_path = 'creating-grid/scrap_points_radius_limit_per_cell_120.csv'
    points = google_places_scrapper.read_points(points_path)
    # random points order:
    points = random.sample(points, 10)
    scrapper = google_places_scrapper.GooglePlacesScrapper(google_places_scrapper.API_KEY, points)
    scrapper.scrap_old(keyword="sklep z e-papierosami")


if __name__ == "__main__":
    main()
