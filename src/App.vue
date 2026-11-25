<template>
  <div class="min-h-screen flex flex-col bg-gradient-to-b from-sky-100 via-sky-50 to-blue-100/70 text-slate-900">
    <!-- Top Header Bar -->
    <header class="sticky top-0 z-30 bg-sky-100/90 backdrop-blur-md border-b border-sky-200/80 shadow-xs">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-sky-600 flex items-center justify-center text-white shadow-sm shadow-sky-300">
            <Baby class="w-6 h-6" />
          </div>
          <div>
            <h1 class="text-lg font-extrabold tracking-tight text-sky-950">DiaperScout</h1>
            <p class="text-xs text-sky-800/80 hidden sm:block">
              Retailer Pricing, Standardized Age-Range Sizing &amp; Brand Ratings
            </p>
          </div>
        </div>

        <!-- Last Updated Timestamp -->
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-sky-200/60 border border-sky-300/70 text-xs text-sky-900">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Last updated: <strong class="text-sky-950 tabular-nums">{{ formattedScrapeTime }}</strong></span>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <!-- Collapsible Filter Console (Collapsed by Default) -->
      <section class="bg-sky-50/90 rounded-2xl border border-sky-200 shadow-sm overflow-hidden transition-all">
        <!-- Always-Visible Filter Bar / Toggle Header -->
        <div
          @click="filtersExpanded = !filtersExpanded"
          class="p-4 sm:px-5 flex flex-wrap items-center justify-between gap-3 cursor-pointer hover:bg-sky-100/70 transition-colors select-none"
        >
          <div class="flex flex-wrap items-center gap-2.5">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-sky-600 text-white text-xs font-bold shadow-xs">
              <SlidersHorizontal class="w-3.5 h-3.5" />
              <span>Filters &amp; Preferences</span>
            </div>

            <!-- Active Filter Summary Pills -->
            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-sky-200/70 text-sky-950 text-xs font-semibold">
              <Calendar class="w-3.5 h-3.5 text-sky-700" />
              <span>{{ activeSizeSummaryLabel }}</span>
            </span>

            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-sky-200/70 text-sky-950 text-xs font-semibold">
              <Store class="w-3.5 h-3.5 text-sky-700" />
              <span>{{ selectedStores.length === allStores.length ? `All ${allStores.length} Stores` : `${selectedStores.length} Stores` }}</span>
            </span>

            <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-sky-200/70 text-sky-950 text-xs font-semibold">
              <Package class="w-3.5 h-3.5 text-sky-700" />
              <span>{{ selectedPackTiers.length === allPackTiers.length ? 'All Pack Sizes' : `${selectedPackTiers.length} Pack Tiers` }}</span>
            </span>

            <span
              v-if="hasCustomFilters"
              @click.stop="resetAllFilters"
              class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-rose-100 text-rose-800 hover:bg-rose-200 text-xs font-bold transition"
            >
              Reset
            </span>
          </div>

          <div class="flex items-center gap-3">
            <!-- Quick Search inside header (stops propagation so typing doesn't collapse) -->
            <div class="relative w-48 sm:w-60" @click.stop>
              <Search class="w-3.5 h-3.5 text-sky-600 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Quick search brand or feature..."
                class="w-full pl-8 pr-3 py-1.5 text-xs rounded-xl border border-sky-300 bg-sky-100/60 text-sky-950 placeholder:text-sky-600/70 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:bg-sky-50"
              />
            </div>

            <button
              type="button"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-sky-300 bg-sky-100 text-sky-900 hover:bg-sky-200/80 text-xs font-bold transition"
            >
              <span>{{ filtersExpanded ? 'Hide Filters' : 'Show Filters' }}</span>
              <ChevronUp v-if="filtersExpanded" class="w-4 h-4 text-sky-700" />
              <ChevronDown v-else class="w-4 h-4 text-sky-700" />
            </button>
          </div>
        </div>

        <!-- Expandable Filter Body -->
        <div v-show="filtersExpanded" class="px-5 pb-5 pt-3 border-t border-sky-200/80 space-y-5 bg-sky-50/60">
          <!-- Row 1: Diaper Size Standardized to Age Ranges -->
          <div>
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
              <div class="flex items-center gap-2">
                <Calendar class="w-4 h-4 text-sky-700" />
                <h2 class="text-xs font-extrabold uppercase tracking-wider text-sky-900">
                  1. Diaper Size (Standardized to Age &amp; Weight Ranges)
                </h2>
              </div>
              <button
                v-if="selectedSize !== 'ALL'"
                @click="selectedSize = 'ALL'"
                class="text-xs font-bold text-sky-700 hover:text-sky-950"
              >
                Show All Ages / Sizes
              </button>
            </div>

            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-2">
              <!-- All Sizes Button -->
              <button
                @click="selectedSize = 'ALL'"
                :class="[
                  'flex flex-col items-start justify-between p-2.5 rounded-xl border text-left transition-all',
                  selectedSize === 'ALL'
                    ? 'bg-sky-600 text-white border-sky-600 shadow-sm ring-2 ring-sky-500/30'
                    : 'bg-sky-100/80 hover:bg-sky-200/70 text-sky-950 border-sky-200'
                ]"
              >
                <span class="text-xs font-bold uppercase tracking-wider opacity-80">All Ages</span>
                <span class="text-base font-extrabold mt-0.5">All Sizes</span>
                <span :class="['text-[11px] mt-1', selectedSize === 'ALL' ? 'text-sky-100' : 'text-sky-700']">
                  0 – 48+ mos
                </span>
              </button>

              <!-- Individual Standardized Age/Size Cards -->
              <button
                v-for="sz in sizesList"
                :key="sz.size_code"
                @click="selectedSize = sz.size_code"
                :class="[
                  'flex flex-col items-start justify-between p-2.5 rounded-xl border text-left transition-all',
                  selectedSize === sz.size_code
                    ? 'bg-sky-600 text-white border-sky-600 shadow-sm ring-2 ring-sky-500/30'
                    : 'bg-sky-100/70 hover:bg-sky-200/70 text-sky-950 border-sky-200'
                ]"
              >
                <span
                  :class="[
                    'inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-tight',
                    selectedSize === sz.size_code
                      ? 'bg-sky-500 text-white'
                      : 'bg-sky-200 text-sky-800'
                  ]"
                >
                  {{ sz.age_group_short }}
                </span>
                <span class="text-sm font-extrabold mt-1">
                  {{ sz.size_code === 'N' ? 'Newborn (N)' : `Size ${sz.size_code}` }}
                </span>
                <span :class="['text-[11px] font-medium mt-0.5', selectedSize === sz.size_code ? 'text-sky-100' : 'text-sky-700']">
                  {{ sz.weight_range_lbs }}
                </span>
              </button>
            </div>
          </div>

          <div class="border-t border-sky-200/70 pt-4 grid grid-cols-1 lg:grid-cols-12 gap-5">
            <!-- Row 2 Left: Target Stores Multi-Select -->
            <div class="lg:col-span-7">
              <div class="flex items-center justify-between mb-2.5">
                <div class="flex items-center gap-2">
                  <Store class="w-4 h-4 text-sky-700" />
                  <h2 class="text-xs font-extrabold uppercase tracking-wider text-sky-900">
                    2. Filter by Retailer Stores
                  </h2>
                </div>
                <div class="flex items-center gap-2 text-xs">
                  <button
                    @click="selectAllStores"
                    class="font-bold text-sky-700 hover:text-sky-950"
                  >
                    Select All ({{ allStores.length }})
                  </button>
                  <span class="text-sky-300">|</span>
                  <button
                    @click="selectNoClubStores"
                    class="font-semibold text-sky-700/80 hover:text-sky-950"
                  >
                    No Membership Only
                  </button>
                </div>
              </div>

              <div class="flex flex-wrap gap-2">
                <button
                  v-for="store in allStores"
                  :key="store.name"
                  @click="toggleStore(store.name)"
                  :class="[
                    'inline-flex items-center gap-2 px-3 py-2 rounded-xl border text-xs font-bold transition-all',
                    selectedStores.includes(store.name)
                      ? 'bg-sky-800 text-white border-sky-800 shadow-xs'
                      : 'bg-sky-100/70 text-sky-800/70 border-sky-200 hover:bg-sky-200/60'
                  ]"
                >
                  <span
                    class="w-2.5 h-2.5 rounded-full shrink-0"
                    :style="{ backgroundColor: store.color }"
                  ></span>
                  <span>{{ store.name }}</span>
                  <span
                    v-if="store.club"
                    :class="[
                      'px-1.5 py-0.2 rounded text-[10px] font-semibold',
                      selectedStores.includes(store.name) ? 'bg-sky-700 text-sky-100' : 'bg-sky-200 text-sky-700'
                    ]"
                  >
                    Club
                  </span>
                  <span
                    :class="[
                      'ml-0.5 px-1.5 py-0.5 rounded-full text-[10px] tabular-nums',
                      selectedStores.includes(store.name) ? 'bg-white/20 text-white' : 'bg-sky-200/80 text-sky-800'
                    ]"
                  >
                    {{ storeCountMap[store.name] || 0 }}
                  </span>
                </button>
              </div>
            </div>

            <!-- Row 2 Right: Pack Size Selector -->
            <div class="lg:col-span-5">
              <div class="flex items-center justify-between mb-2.5">
                <div class="flex items-center gap-2">
                  <Package class="w-4 h-4 text-sky-700" />
                  <h2 class="text-xs font-extrabold uppercase tracking-wider text-sky-900">
                    3. Pack Size Tier
                  </h2>
                </div>
                <button
                  v-if="selectedPackTiers.length < allPackTiers.length"
                  @click="selectedPackTiers = [...allPackTiers]"
                  class="text-xs font-bold text-sky-700 hover:text-sky-950"
                >
                  Reset All Packs
                </button>
              </div>

              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="pack in packTierDetails"
                  :key="pack.name"
                  @click="togglePackTier(pack.name)"
                  :class="[
                    'flex items-center justify-between px-3 py-2 rounded-xl border text-left transition-all',
                    selectedPackTiers.includes(pack.name)
                      ? 'bg-sky-200/80 border-sky-400 text-sky-950 font-semibold'
                      : 'bg-sky-100/50 border-sky-200 text-sky-700/70 hover:bg-sky-100'
                  ]"
                >
                  <div class="truncate pr-1">
                    <div class="text-xs font-bold truncate">{{ pack.shortLabel }}</div>
                    <div class="text-[10px] opacity-80">{{ pack.countRange }}</div>
                  </div>
                  <Check
                    v-if="selectedPackTiers.includes(pack.name)"
                    class="w-4 h-4 text-sky-700 shrink-0"
                  />
                </button>
              </div>
            </div>
          </div>

          <!-- Row 3: Brand & Feature Filters -->
          <div class="border-t border-sky-200/70 pt-4 flex flex-wrap items-center justify-between gap-3">
            <div class="flex flex-wrap items-center gap-2">
              <!-- Brand Select -->
              <select
                v-model="selectedBrand"
                class="px-3 py-1.5 text-xs font-semibold rounded-xl border border-sky-300 bg-sky-100/80 text-sky-950 focus:outline-none focus:ring-2 focus:ring-sky-500"
              >
                <option value="ALL">All Brands ({{ brandsList.length }})</option>
                <option v-for="b in brandsList" :key="b.brand_id" :value="b.brand_id">
                  {{ b.brand_name }} — {{ b.line_name }} ({{ b.rating }}★)
                </option>
              </select>

              <!-- Quick Feature Pills -->
              <button
                @click="onlyInStock = !onlyInStock"
                :class="[
                  'px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition',
                  onlyInStock
                    ? 'bg-emerald-100 border-emerald-400 text-emerald-900'
                    : 'bg-sky-100/70 border-sky-200 text-sky-800 hover:bg-sky-200/60'
                ]"
              >
                In Stock Only
              </button>

              <button
                @click="onlyEcoFriendly = !onlyEcoFriendly"
                :class="[
                  'px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition',
                  onlyEcoFriendly
                    ? 'bg-teal-100 border-teal-400 text-teal-900'
                    : 'bg-sky-100/70 border-sky-200 text-sky-800 hover:bg-sky-200/60'
                ]"
              >
                🌱 Plant-Based / Eco
              </button>

              <button
                @click="onlyOnSale = !onlyOnSale"
                :class="[
                  'px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition',
                  onlyOnSale
                    ? 'bg-amber-100 border-amber-400 text-amber-900'
                    : 'bg-sky-100/70 border-sky-200 text-sky-800 hover:bg-sky-200/60'
                ]"
              >
                🏷️ On Sale / Promo
              </button>
            </div>

            <button
              @click="resetAllFilters"
              class="text-xs font-bold text-sky-700 hover:text-sky-950 underline"
            >
              Reset All Filters
            </button>
          </div>
        </div>
      </section>

      <!-- Active Age Range Standard Banner (when specific size selected) -->
      <div
        v-if="activeSizeInfo"
        class="bg-gradient-to-r from-sky-600 to-blue-600 rounded-2xl p-4 text-white shadow-sm flex flex-wrap items-center justify-between gap-4"
      >
        <div class="flex items-center gap-3">
          <div class="w-11 h-11 rounded-xl bg-white/15 backdrop-blur flex items-center justify-center font-extrabold text-lg">
            {{ activeSizeInfo.size_code }}
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="font-extrabold text-base">{{ activeSizeInfo.size_label }}</h3>
              <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-white/20">
                {{ activeSizeInfo.age_range }}
              </span>
            </div>
            <p class="text-xs text-sky-100 mt-0.5">
              Standardized Weight: <strong>{{ activeSizeInfo.weight_range_lbs }}</strong> ({{ activeSizeInfo.weight_range_kg }}) •
              Typical Usage: <strong>~{{ activeSizeInfo.daily_usage_est }} diapers/day</strong> (~{{ activeSizeInfo.daily_usage_est * 30 }}/month)
            </p>
          </div>
        </div>
        <div class="text-right">
          <div class="text-xs text-sky-100">Best Unit Price in {{ activeSizeInfo.size_label }}</div>
          <div class="text-xl font-extrabold tabular-nums" v-if="bestUnitOffer">
            ${{ bestUnitOffer.price_per_diaper.toFixed(2) }}<span class="text-xs font-normal">/diaper</span>
            <span class="text-xs font-semibold text-sky-100 ml-1">
              ({{ bestUnitOffer.brand_name }} @ {{ bestUnitOffer.store }})
            </span>
          </div>
        </div>
      </div>

      <!-- KPI Summary Cards -->
      <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Best Unit Value -->
        <div class="bg-sky-50/90 rounded-2xl border border-sky-200 p-4 shadow-xs">
          <div class="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-sky-700/80">
            <span>Best Unit Value</span>
            <TrendingDown class="w-4 h-4 text-emerald-600" />
          </div>
          <div v-if="bestUnitOffer" class="mt-2">
            <div class="flex items-baseline gap-1.5">
              <span class="text-2xl font-extrabold text-sky-950 tabular-nums">
                ${{ bestUnitOffer.price_per_diaper.toFixed(2) }}
              </span>
              <span class="text-xs font-semibold text-sky-700">/ diaper</span>
            </div>
            <p class="text-xs font-semibold text-sky-900 mt-1 truncate">
              {{ bestUnitOffer.brand_name }} {{ bestUnitOffer.line_name }} ({{ bestUnitOffer.size_label }})
            </p>
            <p class="text-[11px] text-emerald-700 font-semibold mt-0.5">
              {{ bestUnitOffer.store }} • ${{ bestUnitOffer.price.toFixed(2) }} for {{ bestUnitOffer.diaper_count }} ct
            </p>
          </div>
          <div v-else class="mt-2 text-sm text-sky-600">No matching offers</div>
        </div>

        <!-- Average Price & Monthly Cost -->
        <div class="bg-sky-50/90 rounded-2xl border border-sky-200 p-4 shadow-xs">
          <div class="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-sky-700/80">
            <span>Market Average</span>
            <DollarSign class="w-4 h-4 text-sky-600" />
          </div>
          <div v-if="filteredPrices.length" class="mt-2">
            <div class="flex items-baseline gap-1.5">
              <span class="text-2xl font-extrabold text-sky-950 tabular-nums">
                ${{ averageUnitCost.toFixed(2) }}
              </span>
              <span class="text-xs font-semibold text-sky-700">/ diaper avg</span>
            </div>
            <p class="text-xs font-semibold text-sky-900 mt-1">
              Est. Monthly Spend: <span class="text-sky-700 font-extrabold tabular-nums">${{ averageMonthlyCost.toFixed(2) }}/mo</span>
            </p>
            <p class="text-[11px] text-sky-700/80 mt-0.5">
              Across {{ filteredPrices.length }} matching store options
            </p>
          </div>
          <div v-else class="mt-2 text-sm text-sky-600">No matching offers</div>
        </div>

        <!-- Highest Rated Brand in Filter -->
        <div class="bg-sky-50/90 rounded-2xl border border-sky-200 p-4 shadow-xs">
          <div class="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-sky-700/80">
            <span>Highest Rated Choice</span>
            <Star class="w-4 h-4 text-amber-500 fill-amber-400" />
          </div>
          <div v-if="topRatedBrandInFilter" class="mt-2">
            <div class="flex items-baseline gap-1.5">
              <span class="text-2xl font-extrabold text-sky-950 tabular-nums">
                {{ topRatedBrandInFilter.rating.toFixed(1) }} ★
              </span>
              <span class="text-xs font-semibold text-sky-700">
                ({{ topRatedBrandInFilter.review_count.toLocaleString() }} reviews)
              </span>
            </div>
            <p class="text-xs font-semibold text-sky-900 mt-1 truncate">
              {{ topRatedBrandInFilter.brand_name }} {{ topRatedBrandInFilter.line_name }}
            </p>
            <p class="text-[11px] text-sky-700/80 mt-0.5 truncate">
              Softness {{ topRatedBrandInFilter.softness_score }}/10 • Leak Guard {{ topRatedBrandInFilter.leak_protection_score }}/10
            </p>
          </div>
          <div v-else class="mt-2 text-sm text-sky-600">No matching brands</div>
        </div>

        <!-- Lowest Price Store -->
        <div class="bg-sky-50/90 rounded-2xl border border-sky-200 p-4 shadow-xs">
          <div class="flex items-center justify-between text-xs font-bold uppercase tracking-wider text-sky-700/80">
            <span>Cheapest Retailer (Avg)</span>
            <Award class="w-4 h-4 text-blue-600" />
          </div>
          <div v-if="storeLeaderboard.length" class="mt-2">
            <div class="flex items-baseline gap-1.5">
              <span class="text-2xl font-extrabold text-sky-950">
                {{ storeLeaderboard[0].store }}
              </span>
              <span class="text-xs font-bold text-emerald-700 tabular-nums">
                ${{ storeLeaderboard[0].avgUnit.toFixed(2) }}/ea
              </span>
            </div>
            <p class="text-xs font-semibold text-sky-900 mt-1">
              {{ storeLeaderboard[0].skuCount }} matching options available
            </p>
            <p class="text-[11px] text-sky-700/80 mt-0.5">
              Save up to {{ maxPotentialSavingsPct }}% vs highest store option
            </p>
          </div>
          <div v-else class="mt-2 text-sm text-sky-600">No store data</div>
        </div>
      </section>

      <!-- Navigation Tabs -->
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-sky-200 pb-3">
        <div class="flex items-center gap-2">
          <button
            @click="activeTab = 'offers'"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all',
              activeTab === 'offers'
                ? 'bg-sky-600 text-white shadow-xs'
                : 'bg-sky-50/90 text-sky-800 border border-sky-200 hover:bg-sky-100'
            ]"
          >
            <Layers class="w-4 h-4" />
            <span>Store Pricing &amp; Packs ({{ filteredPrices.length }})</span>
          </button>

          <button
            @click="activeTab = 'brands'"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all',
              activeTab === 'brands'
                ? 'bg-sky-600 text-white shadow-xs'
                : 'bg-sky-50/90 text-sky-800 border border-sky-200 hover:bg-sky-100'
            ]"
          >
            <Sparkles class="w-4 h-4" />
            <span>Brand Ratings, Features &amp; Descriptions ({{ filteredBrands.length }})</span>
          </button>

          <button
            @click="activeTab = 'matrix'"
            :class="[
              'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all',
              activeTab === 'matrix'
                ? 'bg-sky-600 text-white shadow-xs'
                : 'bg-sky-50/90 text-sky-800 border border-sky-200 hover:bg-sky-100'
            ]"
          >
            <BarChart3 class="w-4 h-4" />
            <span>Store &amp; Age-Size Cost Matrix</span>
          </button>
        </div>

        <p v-if="activeTab === 'offers'" class="text-xs text-sky-800/80 font-medium">
          Tip: Click any column header below to sort
        </p>
      </div>

      <!-- TAB 1: LIVE STORE PRICING & PACKS -->
      <section v-if="activeTab === 'offers'" class="space-y-4">
        <div v-if="filteredPrices.length === 0" class="bg-sky-50/90 rounded-2xl border border-sky-200 p-12 text-center">
          <p class="text-base font-bold text-sky-950">No diaper packs match your current filters.</p>
          <p class="text-xs text-sky-700 mt-1">Try enabling more retailer stores or resetting the pack size filter.</p>
          <button
            @click="resetAllFilters"
            class="mt-4 px-4 py-2 rounded-xl text-xs font-bold bg-sky-600 text-white hover:bg-sky-700"
          >
            Reset All Filters
          </button>
        </div>

        <div v-else class="bg-sky-50/90 rounded-2xl border border-sky-200 shadow-sm overflow-hidden">
          <!-- Mobile Sortable Header Chips (< md screens) -->
          <div class="md:hidden bg-sky-200/60 border-b border-sky-200 p-3">
            <div class="text-[10px] font-extrabold uppercase tracking-wider text-sky-800 mb-2">
              Tap a column to sort:
            </div>
            <div class="flex flex-wrap gap-1.5">
              <button
                v-for="col in sortableColumns"
                :key="col.field"
                @click="toggleSort(col.field)"
                :class="[
                  'inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-[11px] font-bold border transition-all',
                  sortField === col.field
                    ? 'bg-sky-700 text-white border-sky-700 shadow-xs'
                    : 'bg-sky-50/90 text-sky-900 border-sky-300 hover:bg-sky-100'
                ]"
              >
                <span>{{ col.label }}</span>
                <component
                  :is="getSortIcon(col.field)"
                  class="w-3 h-3"
                  :class="sortField === col.field ? 'text-white' : 'text-sky-600/70'"
                />
              </button>
            </div>
          </div>

          <!-- Mobile Stacked Cards (< md screens, zero horizontal scroll) -->
          <div class="md:hidden divide-y divide-sky-200/80">
            <div
              v-for="(item, idx) in paginatedPrices"
              :key="`${item.sku_id}-mobile`"
              class="p-4 space-y-3 hover:bg-sky-100/60 transition-colors"
            >
              <!-- Card Top: Brand, Badge & Unit Cost Pill -->
              <div class="flex items-start justify-between gap-2">
                <button
                  @click="openBrandDetail(item.brand_id)"
                  class="text-left flex-1 min-w-0"
                >
                  <div class="flex flex-wrap items-center gap-1.5">
                    <span class="font-extrabold text-sky-950 text-sm">
                      {{ item.brand_name }} {{ item.line_name }}
                    </span>
                    <span
                      v-if="idx === 0 && sortField === 'unit' && sortDirection === 'asc' && currentPage === 1"
                      class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300"
                    >
                      #1 Best Value
                    </span>
                  </div>
                  <p class="text-[11px] text-sky-800/85 line-clamp-1 mt-0.5">
                    {{ brandMap[item.brand_id]?.description }}
                  </p>
                </button>

                <div class="text-right shrink-0 tabular-nums">
                  <span
                    :class="[
                      'inline-flex items-center px-2.5 py-1 rounded-xl text-xs font-extrabold',
                      getUnitCostBadgeClass(item.price_per_diaper)
                    ]"
                  >
                    ${{ item.price_per_diaper.toFixed(2) }}/ea
                  </span>
                  <div class="text-[10px] text-sky-700/80 mt-0.5">
                    ({{ (item.price_per_diaper * 100).toFixed(1) }}¢ / diaper)
                  </div>
                </div>
              </div>

              <!-- Card Middle Grid: Store, Size/Age, Pack Count, Box & Monthly Price -->
              <div class="grid grid-cols-2 gap-2.5 bg-sky-100/80 p-3 rounded-xl border border-sky-200/80 text-xs">
                <div>
                  <div class="text-[10px] font-bold uppercase text-sky-700/80">Retailer Store</div>
                  <div class="inline-flex items-center gap-1.5 font-extrabold text-sky-950 mt-0.5">
                    <span
                      class="w-2.5 h-2.5 rounded-full shrink-0"
                      :style="{ backgroundColor: storeColorMap[item.store] || '#0284c7' }"
                    ></span>
                    <span>{{ item.store }}</span>
                  </div>
                  <div v-if="item.promo_badge" class="mt-0.5 text-[10px] font-semibold text-amber-800 truncate">
                    {{ item.promo_badge }}
                  </div>
                </div>

                <div>
                  <div class="text-[10px] font-bold uppercase text-sky-700/80">Size &amp; Age Range</div>
                  <div class="font-extrabold text-sky-950 mt-0.5">
                    {{ item.size_label }}
                  </div>
                  <div class="text-[11px] font-semibold text-sky-700 truncate">
                    {{ item.age_group_short }} ({{ item.weight_range_lbs }})
                  </div>
                </div>

                <div>
                  <div class="text-[10px] font-bold uppercase text-sky-700/80">Pack Size &amp; Count</div>
                  <div class="font-extrabold text-sky-950 mt-0.5">
                    {{ item.diaper_count }} diapers
                  </div>
                  <div class="text-[11px] text-sky-800/80 truncate">
                    {{ item.pack_size_tier }}
                  </div>
                </div>

                <div class="tabular-nums">
                  <div class="text-[10px] font-bold uppercase text-sky-700/80">Box &amp; Est. Monthly</div>
                  <div class="flex items-baseline gap-1.5 mt-0.5">
                    <span class="font-extrabold text-sky-950 text-sm">${{ item.price.toFixed(2) }}</span>
                    <span v-if="item.on_sale" class="text-[11px] text-sky-600 line-through">
                      ${{ item.regular_price.toFixed(2) }}
                    </span>
                  </div>
                  <div class="text-[11px] font-semibold text-sky-800">
                    ~${{ item.monthly_cost_est.toFixed(2) }}/mo
                  </div>
                </div>
              </div>

              <!-- Feature Chips -->
              <div class="flex flex-wrap gap-1">
                <span
                  v-for="feat in (brandMap[item.brand_id]?.featuresList || []).slice(0, 3)"
                  :key="feat"
                  class="px-2 py-0.5 rounded-md bg-sky-200/60 text-sky-900 text-[10px] font-medium"
                >
                  {{ feat }}
                </span>
                <button
                  @click="openBrandDetail(item.brand_id)"
                  class="px-2 py-0.5 rounded-md bg-sky-200 text-sky-800 text-[10px] font-bold"
                >
                  More Details →
                </button>
              </div>

              <!-- Card Footer: Rating, Stock Status & Direct Store Link -->
              <div class="flex items-center justify-between pt-1 text-xs">
                <div class="flex items-center gap-2">
                  <div class="inline-flex items-center gap-1 font-bold text-sky-950">
                    <Star class="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
                    <span class="tabular-nums">{{ item.rating.toFixed(1) }}</span>
                    <span class="text-[11px] font-normal text-sky-700/80 tabular-nums">
                      ({{ item.review_count.toLocaleString() }})
                    </span>
                  </div>

                  <span
                    :class="[
                      'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold',
                      item.availability === 'In Stock'
                        ? 'bg-emerald-100 text-emerald-800'
                        : item.availability === 'Low Stock'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-rose-100 text-rose-800'
                    ]"
                  >
                    <span
                      class="w-1.5 h-1.5 rounded-full"
                      :class="
                        item.availability === 'In Stock'
                          ? 'bg-emerald-500'
                          : item.availability === 'Low Stock'
                          ? 'bg-amber-500'
                          : 'bg-rose-500'
                      "
                    ></span>
                    {{ item.availability }}
                  </span>
                </div>

                <a
                  :href="item.product_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-sky-600 text-white text-[11px] font-bold hover:bg-sky-700 shadow-2xs"
                >
                  <span>Check {{ item.store }}</span>
                  <ExternalLink class="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>

          <!-- Desktop Table (md and larger screens) -->
          <div class="hidden md:block overflow-x-auto">
            <table class="w-full text-left border-collapse">
              <thead>
                <tr class="bg-sky-200/60 border-b border-sky-200 text-[11px] font-extrabold uppercase tracking-wider text-sky-900 select-none">
                  <th
                    @click="toggleSort('brand')"
                    class="py-3.5 px-4 cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center gap-1">
                      <span>Diaper Brand &amp; Features</span>
                      <component :is="getSortIcon('brand')" class="w-3.5 h-3.5" :class="sortField === 'brand' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('store')"
                    class="py-3.5 px-3 cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center gap-1">
                      <span>Store</span>
                      <component :is="getSortIcon('store')" class="w-3.5 h-3.5" :class="sortField === 'store' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('size')"
                    class="py-3.5 px-3 cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center gap-1">
                      <span>Size &amp; Age Standard</span>
                      <component :is="getSortIcon('size')" class="w-3.5 h-3.5" :class="sortField === 'size' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('count')"
                    class="py-3.5 px-3 cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center gap-1">
                      <span>Pack Tier &amp; Count</span>
                      <component :is="getSortIcon('count')" class="w-3.5 h-3.5" :class="sortField === 'count' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('price')"
                    class="py-3.5 px-3 text-right cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center justify-end gap-1">
                      <span>Box Price</span>
                      <component :is="getSortIcon('price')" class="w-3.5 h-3.5" :class="sortField === 'price' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('unit')"
                    class="py-3.5 px-3 text-right cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center justify-end gap-1">
                      <span>Cost / Diaper</span>
                      <component :is="getSortIcon('unit')" class="w-3.5 h-3.5" :class="sortField === 'unit' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('monthly')"
                    class="py-3.5 px-3 text-right cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center justify-end gap-1">
                      <span>Est. Monthly</span>
                      <component :is="getSortIcon('monthly')" class="w-3.5 h-3.5" :class="sortField === 'monthly' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('rating')"
                    class="py-3.5 px-3 cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center gap-1">
                      <span>Rating</span>
                      <component :is="getSortIcon('rating')" class="w-3.5 h-3.5" :class="sortField === 'rating' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>

                  <th
                    @click="toggleSort('availability')"
                    class="py-3.5 px-4 text-right cursor-pointer hover:bg-sky-200/90 transition-colors"
                  >
                    <div class="inline-flex items-center justify-end gap-1">
                      <span>Status &amp; Link</span>
                      <component :is="getSortIcon('availability')" class="w-3.5 h-3.5" :class="sortField === 'availability' ? 'text-sky-700' : 'text-sky-500/60'" />
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-sky-200/60 text-xs">
                <tr
                  v-for="(item, idx) in paginatedPrices"
                  :key="item.sku_id"
                  class="hover:bg-sky-100/80 transition-colors group"
                >
                  <!-- Brand & Features -->
                  <td class="py-3.5 px-4 max-w-xs">
                    <div class="flex items-start gap-2.5">
                      <button
                        @click="openBrandDetail(item.brand_id)"
                        class="text-left group-hover:text-sky-700 transition-colors"
                      >
                        <div class="font-extrabold text-sky-950 text-sm flex items-center gap-1.5">
                          <span>{{ item.brand_name }} {{ item.line_name }}</span>
                          <span
                            v-if="idx === 0 && sortField === 'unit' && sortDirection === 'asc' && currentPage === 1"
                            class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 border border-emerald-300"
                          >
                            #1 Best Value
                          </span>
                        </div>
                        <p class="text-[11px] text-sky-800/80 line-clamp-1 mt-0.5">
                          {{ brandMap[item.brand_id]?.description }}
                        </p>
                      </button>
                    </div>
                    <div class="flex flex-wrap gap-1 mt-1.5">
                      <span
                        v-for="feat in (brandMap[item.brand_id]?.featuresList || []).slice(0, 3)"
                        :key="feat"
                        class="px-1.5 py-0.5 rounded bg-sky-200/60 text-sky-900 text-[10px] font-medium"
                      >
                        {{ feat }}
                      </span>
                      <button
                        @click="openBrandDetail(item.brand_id)"
                        class="px-1.5 py-0.5 rounded bg-sky-200 text-sky-800 text-[10px] font-bold hover:bg-sky-300/80"
                      >
                        Details →
                      </button>
                    </div>
                  </td>

                  <!-- Store -->
                  <td class="py-3.5 px-3 whitespace-nowrap">
                    <div class="inline-flex items-center gap-1.5 font-bold text-sky-950">
                      <span
                        class="w-2.5 h-2.5 rounded-full"
                        :style="{ backgroundColor: storeColorMap[item.store] || '#0284c7' }"
                      ></span>
                      <span>{{ item.store }}</span>
                    </div>
                    <div v-if="item.membership_required" class="text-[10px] text-sky-700/80 font-medium">
                      Membership Club
                    </div>
                    <div v-if="item.promo_badge" class="mt-0.5 inline-block px-1.5 py-0.5 rounded bg-amber-100/90 border border-amber-300 text-amber-900 text-[10px] font-semibold">
                      {{ item.promo_badge }}
                    </div>
                  </td>

                  <!-- Size & Age Standard -->
                  <td class="py-3.5 px-3 whitespace-nowrap">
                    <div class="font-extrabold text-sky-950">
                      {{ item.size_label }}
                    </div>
                    <div class="text-[11px] font-semibold text-sky-700">
                      {{ item.age_range }}
                    </div>
                    <div class="text-[10px] text-sky-700/75">
                      {{ item.weight_range_lbs }}
                    </div>
                  </td>

                  <!-- Pack Tier & Count -->
                  <td class="py-3.5 px-3 whitespace-nowrap">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold bg-sky-200/70 text-sky-950">
                      {{ item.diaper_count }} diapers
                    </span>
                    <div class="text-[11px] text-sky-800/80 mt-0.5">
                      {{ item.pack_size_tier }}
                    </div>
                  </td>

                  <!-- Box Price -->
                  <td class="py-3.5 px-3 text-right whitespace-nowrap tabular-nums">
                    <div class="text-sm font-extrabold text-sky-950">
                      ${{ item.price.toFixed(2) }}
                    </div>
                    <div v-if="item.on_sale" class="text-[11px] text-sky-600 line-through">
                      ${{ item.regular_price.toFixed(2) }}
                    </div>
                  </td>

                  <!-- Cost / Diaper -->
                  <td class="py-3.5 px-3 text-right whitespace-nowrap tabular-nums">
                    <span
                      :class="[
                        'inline-flex items-center px-2 py-1 rounded-lg text-xs font-extrabold',
                        getUnitCostBadgeClass(item.price_per_diaper)
                      ]"
                    >
                      ${{ item.price_per_diaper.toFixed(2) }}/ea
                    </span>
                    <div class="text-[10px] text-sky-700/80 mt-0.5">
                      ({{ (item.price_per_diaper * 100).toFixed(1) }}¢)
                    </div>
                  </td>

                  <!-- Est Monthly Cost -->
                  <td class="py-3.5 px-3 text-right whitespace-nowrap tabular-nums">
                    <div class="font-bold text-sky-950">
                      ${{ item.monthly_cost_est.toFixed(2) }}/mo
                    </div>
                    <div class="text-[10px] text-sky-700/80">
                      @ {{ item.daily_usage_est }}/day
                    </div>
                  </td>

                  <!-- Rating -->
                  <td class="py-3.5 px-3 whitespace-nowrap">
                    <div class="flex items-center gap-1 font-bold text-sky-950">
                      <Star class="w-3.5 h-3.5 text-amber-500 fill-amber-400" />
                      <span class="tabular-nums">{{ item.rating.toFixed(1) }}</span>
                    </div>
                    <div class="text-[10px] text-sky-700/80 tabular-nums">
                      {{ item.review_count.toLocaleString() }} reviews
                    </div>
                  </td>

                  <!-- Availability & Link -->
                  <td class="py-3.5 px-4 text-right whitespace-nowrap">
                    <div class="flex flex-col items-end gap-1">
                      <span
                        :class="[
                          'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold',
                          item.availability === 'In Stock'
                            ? 'bg-emerald-100 text-emerald-800'
                            : item.availability === 'Low Stock'
                            ? 'bg-amber-100 text-amber-800'
                            : 'bg-rose-100 text-rose-800'
                        ]"
                      >
                        <span
                          class="w-1.5 h-1.5 rounded-full"
                          :class="
                            item.availability === 'In Stock'
                              ? 'bg-emerald-500'
                              : item.availability === 'Low Stock'
                              ? 'bg-amber-500'
                              : 'bg-rose-500'
                          "
                        ></span>
                        {{ item.availability }}
                      </span>

                      <a
                        :href="item.product_url"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="inline-flex items-center gap-1 text-[11px] font-bold text-sky-700 hover:text-sky-950"
                      >
                        <span>Check {{ item.store }}</span>
                        <ExternalLink class="w-3 h-3" />
                      </a>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination Footer -->
          <div class="px-4 py-3 bg-sky-100/80 border-t border-sky-200 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div class="text-sky-900">
              Showing <strong class="text-sky-950">{{ paginationStart }}–{{ paginationEnd }}</strong> of
              <strong class="text-sky-950">{{ filteredPrices.length }}</strong> diaper options
            </div>
            <div class="flex items-center gap-1.5">
              <button
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage === 1"
                class="px-3 py-1.5 rounded-lg border border-sky-300 bg-sky-50 font-semibold text-sky-900 disabled:opacity-40 hover:bg-sky-200/60"
              >
                Previous
              </button>
              <span class="px-3 py-1.5 font-bold text-sky-950 tabular-nums">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="px-3 py-1.5 rounded-lg border border-sky-300 bg-sky-50 font-semibold text-sky-900 disabled:opacity-40 hover:bg-sky-200/60"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 2: BRAND RATINGS, FEATURES & DESCRIPTIONS -->
      <section v-if="activeTab === 'brands'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        <div
          v-for="brand in filteredBrands"
          :key="brand.brand_id"
          class="bg-sky-50/90 rounded-2xl border border-sky-200 shadow-xs hover:shadow-md transition-shadow p-5 flex flex-col justify-between"
        >
          <div>
            <!-- Header & Rating -->
            <div class="flex items-start justify-between gap-3">
              <div>
                <span class="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider bg-sky-200/80 text-sky-900">
                  {{ brand.tier }}
                </span>
                <h3 class="text-base font-extrabold text-sky-950 mt-1">
                  {{ brand.brand_name }} — {{ brand.line_name }}
                </h3>
                <p class="text-[11px] text-sky-700/80">{{ brand.full_name }}</p>
              </div>
              <div class="text-right shrink-0 bg-amber-100/80 border border-amber-300 px-2.5 py-1.5 rounded-xl">
                <div class="flex items-center gap-1 text-sm font-extrabold text-amber-950">
                  <Star class="w-4 h-4 text-amber-500 fill-amber-400" />
                  <span class="tabular-nums">{{ brand.rating.toFixed(1) }}</span>
                </div>
                <div class="text-[10px] text-amber-800 font-medium tabular-nums">
                  {{ brand.review_count.toLocaleString() }} reviews
                </div>
              </div>
            </div>

            <!-- Detailed Description -->
            <p class="text-xs text-sky-900/90 leading-relaxed mt-3">
              {{ brand.description }}
            </p>

            <!-- Performance Sub-Scores -->
            <div class="mt-4 space-y-2 bg-sky-100/70 p-3 rounded-xl border border-sky-200/80">
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-sky-900">Absorbency &amp; Overnight</span>
                <div class="flex items-center gap-2">
                  <div class="w-24 h-2 rounded-full bg-sky-200 overflow-hidden">
                    <div class="h-full bg-sky-600 rounded-full" :style="{ width: `${brand.absorbency_score * 10}%` }"></div>
                  </div>
                  <span class="font-bold text-sky-950 tabular-nums w-8 text-right">{{ brand.absorbency_score }}/10</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-sky-900">Cloud Softness &amp; Comfort</span>
                <div class="flex items-center gap-2">
                  <div class="w-24 h-2 rounded-full bg-sky-200 overflow-hidden">
                    <div class="h-full bg-blue-600 rounded-full" :style="{ width: `${brand.softness_score * 10}%` }"></div>
                  </div>
                  <span class="font-bold text-sky-950 tabular-nums w-8 text-right">{{ brand.softness_score }}/10</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-xs">
                <span class="font-semibold text-sky-900">Blowout &amp; Leak Protection</span>
                <div class="flex items-center gap-2">
                  <div class="w-24 h-2 rounded-full bg-sky-200 overflow-hidden">
                    <div class="h-full bg-emerald-600 rounded-full" :style="{ width: `${brand.leak_protection_score * 10}%` }"></div>
                  </div>
                  <span class="font-bold text-sky-950 tabular-nums w-8 text-right">{{ brand.leak_protection_score }}/10</span>
                </div>
              </div>
            </div>

            <!-- Key Features Badges -->
            <div class="mt-4">
              <div class="text-[11px] font-bold uppercase tracking-wider text-sky-700 mb-1.5">
                Verified Diaper Features
              </div>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="feat in brand.featuresList"
                  :key="feat"
                  class="px-2 py-0.5 rounded-lg bg-sky-200/60 text-sky-950 text-[11px] font-medium"
                >
                  ✓ {{ feat }}
                </span>
              </div>
            </div>
          </div>

          <!-- Footer: Stores Carried & Best Live Unit Price -->
          <div class="mt-5 pt-3.5 border-t border-sky-200/80 flex items-center justify-between gap-2">
            <div>
              <div class="text-[10px] font-bold uppercase text-sky-700">Available Retailers</div>
              <div class="flex flex-wrap gap-1 mt-1">
                <span
                  v-for="st in brand.storesList"
                  :key="st"
                  class="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-800 text-white"
                >
                  {{ st }}
                </span>
              </div>
            </div>

            <div class="text-right" v-if="brandBestUnitMap[brand.brand_id]">
              <div class="text-[10px] font-bold uppercase text-sky-700">From Unit Cost</div>
              <div class="text-base font-extrabold text-emerald-700 tabular-nums">
                ${{ brandBestUnitMap[brand.brand_id].toFixed(2) }}/ea
              </div>
              <button
                @click="filterByBrandOffers(brand.brand_id)"
                class="text-[11px] font-bold text-sky-700 hover:text-sky-950"
              >
                Compare Packs →
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 3: STORE & AGE-SIZE COST MATRIX -->
      <section v-if="activeTab === 'matrix'" class="space-y-6">
        <!-- Store Leaderboard Table -->
        <div class="bg-sky-50/90 rounded-2xl border border-sky-200 shadow-xs p-5">
          <h3 class="text-sm font-extrabold uppercase tracking-wider text-sky-950 mb-1">
            Retailer Unit Price Comparison (Meijer, Target, Costco, Walmart, Sam's Club, Kroger, Amazon)
          </h3>
          <p class="text-xs text-sky-800/80 mb-4">
            Comparing lowest and average per-diaper unit pricing across your selected size and pack filters.
          </p>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="(st, index) in storeLeaderboard"
              :key="st.store"
              class="p-4 rounded-xl border border-sky-200 bg-sky-100/60 flex flex-col justify-between"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <span
                    class="w-3 h-3 rounded-full"
                    :style="{ backgroundColor: storeColorMap[st.store] || '#0284c7' }"
                  ></span>
                  <span class="font-extrabold text-sm text-sky-950">{{ st.store }}</span>
                </div>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-200 text-sky-900">
                  Rank #{{ index + 1 }}
                </span>
              </div>

              <div class="grid grid-cols-3 gap-2 my-3 pt-2 border-t border-sky-200 text-center">
                <div>
                  <div class="text-[10px] text-sky-700 font-bold uppercase">Lowest $/ea</div>
                  <div class="text-sm font-extrabold text-emerald-700 tabular-nums">${{ st.minUnit.toFixed(2) }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-sky-700 font-bold uppercase">Avg $/ea</div>
                  <div class="text-sm font-extrabold text-sky-950 tabular-nums">${{ st.avgUnit.toFixed(2) }}</div>
                </div>
                <div>
                  <div class="text-[10px] text-sky-700 font-bold uppercase">Avg Box</div>
                  <div class="text-sm font-extrabold text-sky-900 tabular-nums">${{ st.avgBox.toFixed(2) }}</div>
                </div>
              </div>

              <div class="text-[11px] text-sky-800 flex items-center justify-between">
                <span>Best Deal: <strong class="text-sky-950">{{ st.bestBrand }}</strong></span>
                <span class="tabular-nums">{{ st.skuCount }} options</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Standardized Age Range to Diaper Size Reference Table -->
        <div class="bg-sky-50/90 rounded-2xl border border-sky-200 shadow-xs p-5">
          <h3 class="text-sm font-extrabold uppercase tracking-wider text-sky-950 mb-1">
            Standardized Diaper Size &amp; Age Range Cost Breakdown
          </h3>
          <p class="text-xs text-sky-800/80 mb-4">
            Because larger diaper sizes contain fewer diapers per box at the same retail price, unit cost increases as your child grows.
          </p>

          <!-- Mobile Stacked Cards (< md screens) -->
          <div class="md:hidden space-y-2.5">
            <div
              v-for="row in sizeBreakdownRows"
              :key="`${row.size_code}-mobile`"
              @click="selectedSize = row.size_code; activeTab = 'offers'"
              class="p-3.5 rounded-xl border border-sky-200 bg-sky-100/70 active:bg-sky-200/80 cursor-pointer space-y-2"
            >
              <div class="flex items-center justify-between">
                <div>
                  <span class="font-extrabold text-sm text-sky-950">{{ row.size_label }}</span>
                  <span class="ml-2 px-2 py-0.5 rounded-md bg-sky-200 text-sky-900 text-[11px] font-bold">
                    {{ row.age_range }}
                  </span>
                </div>
                <span class="text-xs font-bold text-sky-800">{{ row.weight_range_lbs }}</span>
              </div>

              <div class="grid grid-cols-3 gap-2 pt-2 border-t border-sky-200/80 text-center tabular-nums">
                <div>
                  <div class="text-[10px] font-bold uppercase text-sky-700">Lowest $/ea</div>
                  <div class="text-sm font-extrabold text-emerald-700">
                    {{ row.minUnit ? `$${row.minUnit.toFixed(2)}` : '—' }}
                  </div>
                </div>
                <div>
                  <div class="text-[10px] font-bold uppercase text-sky-700">Avg $/ea</div>
                  <div class="text-sm font-extrabold text-sky-950">
                    {{ row.avgUnit ? `$${row.avgUnit.toFixed(2)}` : '—' }}
                  </div>
                </div>
                <div>
                  <div class="text-[10px] font-bold uppercase text-sky-700">Est. Monthly</div>
                  <div class="text-sm font-extrabold text-sky-700">
                    {{ row.avgMonthly ? `$${row.avgMonthly.toFixed(2)}` : '—' }}
                  </div>
                </div>
              </div>

              <div class="text-[11px] text-sky-800 flex items-center justify-between pt-1">
                <span class="truncate pr-2">Best: <strong class="text-sky-950">{{ row.bestOfferLabel || '—' }}</strong></span>
                <span class="shrink-0 font-semibold text-sky-700">{{ row.daily_usage_est }}/day →</span>
              </div>
            </div>
          </div>

          <!-- Desktop Table (md+ screens) -->
          <div class="hidden md:block overflow-x-auto">
            <table class="w-full text-left border-collapse text-xs">
              <thead>
                <tr class="bg-sky-200/60 border-b border-sky-200 text-[11px] font-bold uppercase text-sky-900">
                  <th class="py-3 px-3">Size</th>
                  <th class="py-3 px-3">Standardized Age Range</th>
                  <th class="py-3 px-3">Baby Weight Range</th>
                  <th class="py-3 px-3 text-right">Est. Diapers / Day</th>
                  <th class="py-3 px-3 text-right">Lowest $/Diaper</th>
                  <th class="py-3 px-3 text-right">Avg $/Diaper</th>
                  <th class="py-3 px-3 text-right">Est. Monthly Cost</th>
                  <th class="py-3 px-3">Best Value Brand &amp; Store</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-sky-200/60">
                <tr
                  v-for="row in sizeBreakdownRows"
                  :key="row.size_code"
                  class="hover:bg-sky-100/80 cursor-pointer"
                  @click="selectedSize = row.size_code; activeTab = 'offers'"
                >
                  <td class="py-3 px-3 font-extrabold text-sky-950">{{ row.size_label }}</td>
                  <td class="py-3 px-3 font-semibold text-sky-700">{{ row.age_range }}</td>
                  <td class="py-3 px-3 text-sky-800">{{ row.weight_range_lbs }}</td>
                  <td class="py-3 px-3 text-right tabular-nums font-medium">{{ row.daily_usage_est }}/day</td>
                  <td class="py-3 px-3 text-right tabular-nums font-extrabold text-emerald-700">
                    {{ row.minUnit ? `$${row.minUnit.toFixed(2)}` : '—' }}
                  </td>
                  <td class="py-3 px-3 text-right tabular-nums font-bold text-sky-950">
                    {{ row.avgUnit ? `$${row.avgUnit.toFixed(2)}` : '—' }}
                  </td>
                  <td class="py-3 px-3 text-right tabular-nums font-bold text-sky-700">
                    {{ row.avgMonthly ? `$${row.avgMonthly.toFixed(2)}/mo` : '—' }}
                  </td>
                  <td class="py-3 px-3 text-sky-900 font-medium">
                    {{ row.bestOfferLabel || '—' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </main>

    <!-- Brand Detail Modal -->
    <div
      v-if="inspectedBrand"
      class="fixed inset-0 z-50 bg-sky-950/50 backdrop-blur-xs flex items-center justify-center p-4"
      @click.self="inspectedBrand = null"
    >
      <div class="bg-sky-50 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl border border-sky-200 p-6 space-y-4">
        <div class="flex items-start justify-between gap-4">
          <div>
            <span class="px-2.5 py-0.5 rounded-full text-xs font-bold bg-sky-200 text-sky-900">
              {{ inspectedBrand.tier }}
            </span>
            <h2 class="text-xl font-extrabold text-sky-950 mt-1">
              {{ inspectedBrand.full_name }}
            </h2>
          </div>
          <button
            @click="inspectedBrand = null"
            class="p-1.5 rounded-lg text-sky-600 hover:text-sky-950 hover:bg-sky-200/60"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <p class="text-sm text-sky-900 leading-relaxed">
          {{ inspectedBrand.description }}
        </p>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-sky-100/80 p-3.5 rounded-xl border border-sky-200 text-center">
          <div>
            <div class="text-[11px] font-bold text-sky-700 uppercase">Rating</div>
            <div class="text-base font-extrabold text-sky-950 mt-0.5">{{ inspectedBrand.rating }} ★</div>
          </div>
          <div>
            <div class="text-[11px] font-bold text-sky-700 uppercase">Absorbency</div>
            <div class="text-base font-extrabold text-sky-700 mt-0.5">{{ inspectedBrand.absorbency_score }}/10</div>
          </div>
          <div>
            <div class="text-[11px] font-bold text-sky-700 uppercase">Softness</div>
            <div class="text-base font-extrabold text-blue-700 mt-0.5">{{ inspectedBrand.softness_score }}/10</div>
          </div>
          <div>
            <div class="text-[11px] font-bold text-sky-700 uppercase">Leak Guard</div>
            <div class="text-base font-extrabold text-emerald-700 mt-0.5">{{ inspectedBrand.leak_protection_score }}/10</div>
          </div>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-sky-700 mb-2">Features &amp; Certifications</h4>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="feat in inspectedBrand.featuresList"
              :key="feat"
              class="px-2.5 py-1 rounded-lg bg-sky-200/70 text-sky-950 text-xs font-semibold"
            >
              ✓ {{ feat }}
            </span>
          </div>
        </div>

        <div class="pt-3 border-t border-sky-200 flex items-center justify-between">
          <div class="text-xs text-sky-800">
            Carried at: <strong class="text-sky-950">{{ inspectedBrand.storesList.join(', ') }}</strong>
          </div>
          <button
            @click="filterByBrandOffers(inspectedBrand.brand_id); inspectedBrand = null"
            class="px-4 py-2 rounded-xl text-xs font-bold bg-sky-600 text-white hover:bg-sky-700"
          >
            View All Packs &amp; Store Prices
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import Papa from 'papaparse'
import {
  Baby,
  Calendar,
  Store,
  Package,
  Search,
  Check,
  Star,
  TrendingDown,
  DollarSign,
  Award,
  Layers,
  Sparkles,
  BarChart3,
  ExternalLink,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  X,
} from 'lucide-vue-next'

const sizesList = ref([])
const brandsList = ref([])
const allPrices = ref([])
const scrapeMeta = ref({ last_scraped: '' })
const isLoadingData = ref(true)

async function loadDataFromSubfolder() {
  isLoadingData.value = true
  try {
    const baseUrl = import.meta.env.BASE_URL || '/'
    const cacheBust = `?t=${Date.now()}`
    const [sizesRes, brandsRes, pricesRes, metaRes] = await Promise.all([
      fetch(`${baseUrl}data/diaper_sizes.csv${cacheBust}`),
      fetch(`${baseUrl}data/diaper_brands.csv${cacheBust}`),
      fetch(`${baseUrl}data/diaper_prices.csv${cacheBust}`),
      fetch(`${baseUrl}data/scrape_metadata.json${cacheBust}`),
    ])

    const [sizesCsvRaw, brandsCsvRaw, pricesCsvRaw, metaJson] = await Promise.all([
      sizesRes.text(),
      brandsRes.text(),
      pricesRes.text(),
      metaRes.ok ? metaRes.json() : Promise.resolve({}),
    ])

    scrapeMeta.value = metaJson || {}

    const parsedSizes = Papa.parse(sizesCsvRaw.trim(), { header: true, skipEmptyLines: true }).data
    const parsedBrands = Papa.parse(brandsCsvRaw.trim(), { header: true, skipEmptyLines: true }).data
    const parsedPrices = Papa.parse(pricesCsvRaw.trim(), { header: true, skipEmptyLines: true }).data

    sizesList.value = parsedSizes
      .map((s) => ({
        ...s,
        daily_usage_est: Number(s.daily_usage_est),
        sort_order: Number(s.sort_order),
      }))
      .sort((a, b) => a.sort_order - b.sort_order)

    brandsList.value = parsedBrands.map((b) => ({
      ...b,
      rating: Number(b.rating),
      review_count: Number(b.review_count),
      absorbency_score: Number(b.absorbency_score),
      softness_score: Number(b.softness_score),
      leak_protection_score: Number(b.leak_protection_score),
      eco_friendly: b.eco_friendly === 'True' || b.eco_friendly === true,
      hypoallergenic: b.hypoallergenic === 'True' || b.hypoallergenic === true,
      wetness_indicator: b.wetness_indicator === 'True' || b.wetness_indicator === true,
      overnight_ready: b.overnight_ready === 'True' || b.overnight_ready === true,
      fragrance_free: b.fragrance_free === 'True' || b.fragrance_free === true,
      featuresList: b.features ? b.features.split('|') : [],
      storesList: b.stores_carried ? b.stores_carried.split('|') : [],
    }))

    allPrices.value = parsedPrices.map((p) => ({
      ...p,
      diaper_count: Number(p.diaper_count),
      price: Number(p.price),
      regular_price: Number(p.regular_price),
      price_per_diaper: Number(p.price_per_diaper),
      monthly_cost_est: Number(p.monthly_cost_est),
      daily_usage_est: Number(p.daily_usage_est),
      rating: Number(p.rating),
      review_count: Number(p.review_count),
      on_sale: p.on_sale === 'True' || p.on_sale === true,
      in_stock: p.in_stock === 'True' || p.in_stock === true,
      membership_required: p.membership_required === 'True' || p.membership_required === true,
    }))
  } catch (err) {
    console.error('Failed to load CSV data from data/ subfolder:', err)
  } finally {
    isLoadingData.value = false
  }
}

onMounted(() => {
  loadDataFromSubfolder()
})

const sizeSortOrderMap = computed(() => {
  const map = {}
  for (const s of sizesList.value) {
    map[s.size_code] = s.sort_order
  }
  return map
})

const brandMap = computed(() => {
  const map = {}
  for (const b of brandsList.value) {
    map[b.brand_id] = b
  }
  return map
})

const allStores = [
  { name: 'Meijer', color: '#dd1321', club: false },
  { name: 'Target', color: '#cc0000', club: false },
  { name: 'Costco', color: '#005dab', club: true },
  { name: 'Walmart', color: '#0071dc', club: false },
  { name: "Sam's Club", color: '#0067a0', club: true },
  { name: 'Kroger', color: '#044194', club: false },
  { name: 'Amazon', color: '#ff9900', club: false },
]

const storeColorMap = Object.fromEntries(allStores.map((s) => [s.name, s.color]))

const packTierDetails = [
  { name: 'Trial / Travel Pack', shortLabel: 'Trial / Small Pack', countRange: '14–44 diapers' },
  { name: 'Jumbo / Regular Pack', shortLabel: 'Jumbo / Regular Box', countRange: '38–140 diapers' },
  { name: 'Super / Enormous Pack', shortLabel: 'Super / Giant Box', countRange: '64–228 diapers' },
  { name: 'Club / Bulk Case', shortLabel: 'Club / Bulk Case', countRange: '92–244 diapers' },
]
const allPackTiers = packTierDetails.map((p) => p.name)

// Filter section collapsed by default
const filtersExpanded = ref(false)

// Interactive Filter States
const selectedSize = ref('ALL')
const selectedStores = ref(allStores.map((s) => s.name))
const selectedPackTiers = ref([...allPackTiers])
const selectedBrand = ref('ALL')
const searchQuery = ref('')
const onlyInStock = ref(false)
const onlyEcoFriendly = ref(false)
const onlyOnSale = ref(false)

// Column header sorting state
const sortField = ref('unit')
const sortDirection = ref('asc')

const sortableColumns = [
  { field: 'unit', label: 'Cost / Diaper' },
  { field: 'price', label: 'Box Price' },
  { field: 'rating', label: 'Rating' },
  { field: 'store', label: 'Store' },
  { field: 'size', label: 'Size & Age' },
  { field: 'count', label: 'Pack Count' },
  { field: 'monthly', label: 'Monthly Est.' },
  { field: 'brand', label: 'Brand' },
  { field: 'availability', label: 'Stock' },
]

const activeTab = ref('offers')
const currentPage = ref(1)
const pageSize = 25

// Modal
const inspectedBrand = ref(null)

const formattedScrapeTime = computed(() => {
  if (!scrapeMeta.value?.last_scraped) return 'Recently'
  try {
    return new Date(scrapeMeta.value.last_scraped).toLocaleString([], {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return scrapeMeta.value.last_scraped
  }
})

const activeSizeSummaryLabel = computed(() => {
  if (selectedSize.value === 'ALL') return 'All Sizes (0–48+ mos)'
  const sz = sizesList.value.find((s) => s.size_code === selectedSize.value)
  return sz ? `${sz.size_label} (${sz.age_group_short})` : `Size ${selectedSize.value}`
})

const hasCustomFilters = computed(() => {
  return (
    selectedSize.value !== 'ALL' ||
    selectedStores.value.length !== allStores.length ||
    selectedPackTiers.value.length !== allPackTiers.length ||
    selectedBrand.value !== 'ALL' ||
    searchQuery.value.trim() !== '' ||
    onlyInStock.value ||
    onlyEcoFriendly.value ||
    onlyOnSale.value
  )
})

function toggleSort(field) {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    // Default descending for rating and diaper count, ascending for prices and text
    sortDirection.value = field === 'rating' || field === 'count' ? 'desc' : 'asc'
  }
}

function getSortIcon(field) {
  if (sortField.value !== field) return ArrowUpDown
  return sortDirection.value === 'asc' ? ArrowUp : ArrowDown
}

// Reset pagination when filters or sorting change
watch(
  [
    selectedSize,
    selectedStores,
    selectedPackTiers,
    selectedBrand,
    searchQuery,
    onlyInStock,
    onlyEcoFriendly,
    onlyOnSale,
    sortField,
    sortDirection,
  ],
  () => {
    currentPage.value = 1
  },
  { deep: true }
)

function toggleStore(storeName) {
  if (selectedStores.value.includes(storeName)) {
    if (selectedStores.value.length > 1) {
      selectedStores.value = selectedStores.value.filter((s) => s !== storeName)
    }
  } else {
    selectedStores.value.push(storeName)
  }
}

function selectAllStores() {
  selectedStores.value = allStores.map((s) => s.name)
}

function selectNoClubStores() {
  selectedStores.value = allStores.filter((s) => !s.club).map((s) => s.name)
}

function togglePackTier(tierName) {
  if (selectedPackTiers.value.includes(tierName)) {
    if (selectedPackTiers.value.length > 1) {
      selectedPackTiers.value = selectedPackTiers.value.filter((t) => t !== tierName)
    }
  } else {
    selectedPackTiers.value.push(tierName)
  }
}

function resetAllFilters() {
  selectedSize.value = 'ALL'
  selectedStores.value = allStores.map((s) => s.name)
  selectedPackTiers.value = [...allPackTiers]
  selectedBrand.value = 'ALL'
  searchQuery.value = ''
  onlyInStock.value = false
  onlyEcoFriendly.value = false
  onlyOnSale.value = false
}

const activeSizeInfo = computed(() => {
  if (selectedSize.value === 'ALL') return null
  return sizesList.value.find((s) => s.size_code === selectedSize.value) || null
})

// Filtered & Header-Sorted SKU rows
const filteredPrices = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()

  const list = allPrices.value.filter((item) => {
    if (selectedSize.value !== 'ALL' && item.size_code !== selectedSize.value) return false
    if (!selectedStores.value.includes(item.store)) return false
    if (!selectedPackTiers.value.includes(item.pack_size_tier)) return false
    if (selectedBrand.value !== 'ALL' && item.brand_id !== selectedBrand.value) return false
    if (onlyInStock.value && !item.in_stock) return false
    if (onlyOnSale.value && !item.on_sale) return false

    const bInfo = brandMap.value[item.brand_id]
    if (onlyEcoFriendly.value && !bInfo?.eco_friendly) return false

    if (q) {
      const haystack = `${item.brand_name} ${item.line_name} ${item.full_name} ${item.store} ${bInfo?.features || ''} ${bInfo?.description || ''}`.toLowerCase()
      if (!haystack.includes(q)) return false
    }
    return true
  })

  const dir = sortDirection.value === 'asc' ? 1 : -1
  const availRank = { 'In Stock': 1, 'Low Stock': 2, 'Out of Stock': 3 }

  return list.sort((a, b) => {
    let cmp = 0
    if (sortField.value === 'brand') {
      cmp = `${a.brand_name} ${a.line_name}`.localeCompare(`${b.brand_name} ${b.line_name}`)
    } else if (sortField.value === 'store') {
      cmp = a.store.localeCompare(b.store)
    } else if (sortField.value === 'size') {
      cmp = (sizeSortOrderMap.value[a.size_code] ?? 0) - (sizeSortOrderMap.value[b.size_code] ?? 0)
    } else if (sortField.value === 'count') {
      cmp = a.diaper_count - b.diaper_count
    } else if (sortField.value === 'price') {
      cmp = a.price - b.price
    } else if (sortField.value === 'unit') {
      cmp = a.price_per_diaper - b.price_per_diaper
    } else if (sortField.value === 'monthly') {
      cmp = a.monthly_cost_est - b.monthly_cost_est
    } else if (sortField.value === 'rating') {
      cmp = a.rating - b.rating || a.review_count - b.review_count
    } else if (sortField.value === 'availability') {
      cmp = (availRank[a.availability] || 9) - (availRank[b.availability] || 9)
    }
    if (cmp === 0) {
      return a.price_per_diaper - b.price_per_diaper
    }
    return cmp * dir
  })
})

// Count per store ignoring store selection filter
const storeCountMap = computed(() => {
  const counts = {}
  for (const s of allStores) counts[s.name] = 0
  for (const item of allPrices.value) {
    if (selectedSize.value !== 'ALL' && item.size_code !== selectedSize.value) continue
    if (!selectedPackTiers.value.includes(item.pack_size_tier)) continue
    if (selectedBrand.value !== 'ALL' && item.brand_id !== selectedBrand.value) continue
    counts[item.store] = (counts[item.store] || 0) + 1
  }
  return counts
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredPrices.value.length / pageSize)))
const paginationStart = computed(() => (filteredPrices.value.length === 0 ? 0 : (currentPage.value - 1) * pageSize + 1))
const paginationEnd = computed(() => Math.min(filteredPrices.value.length, currentPage.value * pageSize))
const paginatedPrices = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredPrices.value.slice(start, start + pageSize)
})

// KPI Metrics
const bestUnitOffer = computed(() => {
  if (!filteredPrices.value.length) return null
  return [...filteredPrices.value].sort((a, b) => a.price_per_diaper - b.price_per_diaper)[0]
})

const averageUnitCost = computed(() => {
  if (!filteredPrices.value.length) return 0
  const sum = filteredPrices.value.reduce((acc, item) => acc + item.price_per_diaper, 0)
  return sum / filteredPrices.value.length
})

const averageMonthlyCost = computed(() => {
  if (!filteredPrices.value.length) return 0
  const sum = filteredPrices.value.reduce((acc, item) => acc + item.monthly_cost_est, 0)
  return sum / filteredPrices.value.length
})

const filteredBrands = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  return brandsList.value.filter((b) => {
    if (selectedBrand.value !== 'ALL' && b.brand_id !== selectedBrand.value) return false
    if (onlyEcoFriendly.value && !b.eco_friendly) return false
    const hasStoreOverlap = b.storesList.some((st) => selectedStores.value.includes(st))
    if (!hasStoreOverlap) return false
    if (q) {
      const hay = `${b.brand_name} ${b.line_name} ${b.full_name} ${b.features} ${b.description}`.toLowerCase()
      if (!hay.includes(q)) return false
    }
    return true
  })
})

const topRatedBrandInFilter = computed(() => {
  if (!filteredBrands.value.length) return null
  return [...filteredBrands.value].sort((a, b) => b.rating - a.rating || b.review_count - a.review_count)[0]
})

const brandBestUnitMap = computed(() => {
  const map = {}
  for (const item of filteredPrices.value) {
    if (!map[item.brand_id] || item.price_per_diaper < map[item.brand_id]) {
      map[item.brand_id] = item.price_per_diaper
    }
  }
  return map
})

const storeLeaderboard = computed(() => {
  const byStore = {}
  for (const item of filteredPrices.value) {
    if (!byStore[item.store]) {
      byStore[item.store] = {
        store: item.store,
        skuCount: 0,
        sumUnit: 0,
        sumBox: 0,
        minUnit: Infinity,
        bestBrand: '',
      }
    }
    const entry = byStore[item.store]
    entry.skuCount += 1
    entry.sumUnit += item.price_per_diaper
    entry.sumBox += item.price
    if (item.price_per_diaper < entry.minUnit) {
      entry.minUnit = item.price_per_diaper
      entry.bestBrand = `${item.brand_name} (${item.size_label})`
    }
  }
  return Object.values(byStore)
    .map((e) => ({
      ...e,
      avgUnit: e.sumUnit / e.skuCount,
      avgBox: e.sumBox / e.skuCount,
    }))
    .sort((a, b) => a.avgUnit - b.avgUnit)
})

const maxPotentialSavingsPct = computed(() => {
  if (filteredPrices.value.length < 2) return 0
  const sorted = [...filteredPrices.value].sort((a, b) => a.price_per_diaper - b.price_per_diaper)
  const lowest = sorted[0].price_per_diaper
  const highest = sorted[sorted.length - 1].price_per_diaper
  return Math.round(((highest - lowest) / highest) * 100)
})

const sizeBreakdownRows = computed(() => {
  return sizesList.value.map((sz) => {
    const matching = allPrices.value.filter(
      (p) =>
        p.size_code === sz.size_code &&
        selectedStores.value.includes(p.store) &&
        selectedPackTiers.value.includes(p.pack_size_tier)
    )
    if (!matching.length) {
      return { ...sz, minUnit: null, avgUnit: null, avgMonthly: null, bestOfferLabel: null }
    }
    const sorted = [...matching].sort((a, b) => a.price_per_diaper - b.price_per_diaper)
    const best = sorted[0]
    const avgUnit = matching.reduce((acc, i) => acc + i.price_per_diaper, 0) / matching.length
    const avgMonthly = matching.reduce((acc, i) => acc + i.monthly_cost_est, 0) / matching.length
    return {
      ...sz,
      minUnit: best.price_per_diaper,
      avgUnit,
      avgMonthly,
      bestOfferLabel: `${best.brand_name} ${best.line_name} @ ${best.store} ($${best.price_per_diaper.toFixed(2)}/ea)`,
    }
  })
})

function getUnitCostBadgeClass(unitCost) {
  if (unitCost <= 0.21) return 'bg-emerald-100 text-emerald-800 border border-emerald-300'
  if (unitCost <= 0.30) return 'bg-sky-200/80 text-sky-950 border border-sky-300'
  if (unitCost <= 0.42) return 'bg-amber-100 text-amber-900 border border-amber-300'
  return 'bg-sky-100 text-sky-800 border border-sky-200'
}

function openBrandDetail(brandId) {
  inspectedBrand.value = brandMap.value[brandId] || null
}

function filterByBrandOffers(brandId) {
  selectedBrand.value = brandId
  activeTab.value = 'offers'
}
</script>
